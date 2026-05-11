#
# Copyright (C) 2026 pdnguyen of HCMC University of Technology VNU-HCM.
# All rights reserved.
# This file is part of the CO3093/CO3094 course.
#
# AsynapRous release
#
# The authors hereby grant to Licensee personal permission to use
# and modify the Licensed Source Code for the sole purpose of studying
# while attending the course
#

"""
daemon.httpadapter
~~~~~~~~~~~~~~~~~

This module provides a http adapter object to manage and persist 
http settings (headers, bodies). The adapter supports both
raw URL paths and RESTful route definitions, and integrates with
Request and Response objects to handle client-server communication.
"""

from .request import Request
from .response import Response
from .dictionary import CaseInsensitiveDict

import json
import asyncio
import inspect

class HttpAdapter:
    """
    A mutable :class:`HTTP adapter <HTTP adapter>` for managing client connections
    and routing requests.

    The `HttpAdapter` class encapsulates the logic for receiving HTTP requests,
    dispatching them to appropriate route handlers, and constructing responses.
    It supports RESTful routing via hooks and integrates with :class:`Request <Request>` 
    and :class:`Response <Response>` objects for full request lifecycle management.

    Attributes:
        ip (str): IP address of the client.
        port (int): Port number of the client.
        conn (socket): Active socket connection.
        connaddr (tuple): Address of the connected client.
        routes (dict): Mapping of route paths to handler functions.
        request (Request): Request object for parsing incoming data.
        response (Response): Response object for building and sending replies.
    """

    __attrs__ = [
        "ip",
        "port",
        "conn",
        "connaddr",
        "routes",
        "request",
        "response",
    ]

    def __init__(self, ip, port, conn, connaddr, routes):
        """
        Initialize a new HttpAdapter instance.

        :param ip (str): IP address of the client.
        :param port (int): Port number of the client.
        :param conn (socket): Active socket connection.
        :param connaddr (tuple): Address of the connected client.
        :param routes (dict): Mapping of route paths to handler functions.
        """

        #: IP address.
        self.ip = ip
        #: Port.
        self.port = port
        #: Connection
        self.conn = conn
        #: Conndection address
        self.connaddr = connaddr
        #: Routes
        self.routes = routes
        #: Request
        self.request = Request()
        #: Response
        self.response = Response()

    def handle_client(self, conn, addr, routes):
        self.conn = conn        
        self.connaddr = addr
        raw_data = conn.recv(4096).decode('utf-8')
        
        if not raw_data:
            conn.close()
            return
            
        self.request.prepare(raw_data, routes)
        req = self.request
        resp = self.response
        resp.request = req

        print(f"[HttpAdapter] Invoke handle_client connection {addr}")

        if req.hook:
            handler = req.hook
            kwargs = {
                "headers": req.headers,
                "body": req.body
            }

            if inspect.iscoroutinefunction(handler):
                response_body = asyncio.run(handler(**kwargs))
            else:
                response_body = handler(**kwargs)

            # Xử lý gán cookie cho endpoint /login
            if req.path == "/login" and req.method == "POST":
                try:
                    data = json.loads(response_body)
                    session_id = data.get("session")
                    if session_id:
                        resp.set_cookie("session", session_id)
                        del data["session"]
                        response_body = json.dumps(data).encode()
                except:
                    pass
            
            if isinstance(response_body, str):
                response_body = response_body.encode()
                
            if response_body.startswith(b"<!DOCTYPE html>") or response_body.startswith(b"<html"):
                resp.headers["Content-Type"] = "text/html"
            else:
                resp.headers["Content-Type"] = "application/json"

            resp._content = response_body
            response = resp.build_response_header(req) + resp._content
        else:
            response = self.response.build_notfound()

        conn.sendall(response)
        conn.close()

    async def handle_client_coroutine(self, reader, writer):
        """
        Handle an incoming client connection using stream reader/writer asynchronously.

        This coroutine reads the HTTP request, parses it, invokes the matching
        route handler (sync or async), builds the response, and sends it back.

        :param reader (StreamReader): asyncio stream reader.
        :param writer (StreamWriter): asyncio stream writer.
        """
        addr = writer.get_extra_info("peername")
        print("[HttpAdapter] Invoke handle_client_coroutine connection {}".format(addr))

        # Request & Response handlers
        req = self.request
        resp = self.response

        # Read request data asynchronously
        msg = await reader.read(4096)
        if not msg:
            writer.close()
            return

        # Parse HTTP request using self.routes (passed from backend closure)
        req.prepare(msg.decode("utf-8"), self.routes)
        resp.request = req

        if req.hook:
            handler = req.hook
            kwargs = {
                "headers": req.headers,
                "body": req.body
            }

            # Support both sync and async handler functions
            if inspect.iscoroutinefunction(handler):
                response_body = await handler(**kwargs)
            else:
                response_body = handler(**kwargs)

            # Handle Set-Cookie for /login endpoint
            if req.path == "/login" and req.method == "POST":
                try:
                    data = json.loads(response_body)
                    session_id = data.get("session")
                    if session_id:
                        resp.set_cookie("session", session_id)
                        del data["session"]
                        response_body = json.dumps(data).encode()
                except:
                    pass

            if isinstance(response_body, str):
                response_body = response_body.encode()

            if response_body.startswith(b"<!DOCTYPE html>") or response_body.startswith(b"<html"):
                resp.headers["Content-Type"] = "text/html"
            else:
                resp.headers["Content-Type"] = "application/json"

            resp._content = response_body
            response = resp.build_response_header(req) + resp._content
        else:
            response = resp.build_notfound()

        # Send response asynchronously and close connection
        writer.write(response)
        await writer.drain()
        writer.close()

    def extract_cookies(self, req):
        """
        Build cookies from the :class:`Request <Request>` headers.

        :param req:(Request) The :class:`Request <Request>` object.
        :rtype: cookies - A dictionary of cookie key-value pairs.
        """
        cookies = {}
        headers = req.headers if hasattr(req, 'headers') else []
        for header in headers:
            if header.startswith("Cookie:"):
                cookie_str = header.split(":", 1)[1].strip()
                for pair in cookie_str.split(";"):
                    key, value = pair.strip().split("=")
                    cookies[key] = value
        return cookies

    def build_response(self, req, resp):
        """Builds a :class:`Response <Response>` object 

        :param req: The :class:`Request <Request>` used to generate the response.
        :param resp: The  response object.
        :rtype: Response
        """
        response = Response()

        # Set encoding.
        response.raw = resp
        response.reason = response.raw.reason if hasattr(response.raw, 'reason') else ''

        if isinstance(req.url, bytes):
            response.url = req.url.decode("utf-8")
        else:
            response.url = req.url

        # Add new cookies from the server.
        response.cookies = self.extract_cookies(req)

        # Give the Response some context.
        response.request = req
        response.connection = self

        return response

    def build_json_response(self, req, resp):
        """Builds a :class:`Response <Response>` object from JSON data

        :param req: The :class:`Request <Request>` used to generate the response.
        :param resp: The  response object.
        :rtype: Response
        """
        response = Response(req)

        # Set encoding.
        response.raw = resp

        if isinstance(req.url, bytes):
            response.url = req.url.decode("utf-8")
        else:
            response.url = req.url

        # Give the Response some context.
        response.request = req
        response.connection = self

        return response


    # def get_connection(self, url, proxies=None):
        # """Returns a url connection for the given URL. 

        # :param url: The URL to connect to.
        # :param proxies: (optional) A Requests-style dictionary of proxies used on this request.
        # :rtype: int
        # """

        # proxy = select_proxy(url, proxies)

        # if proxy:
            # proxy = prepend_scheme_if_needed(proxy, "http")
            # proxy_url = parse_url(proxy)
            # if not proxy_url.host:
                # raise InvalidProxyURL(
                    # "Please check proxy URL. It is malformed "
                    # "and could be missing the host."
                # )
            # proxy_manager = self.proxy_manager_for(proxy)
            # conn = proxy_manager.connection_from_url(url)
        # else:
            # # Only scheme should be lower case
            # parsed = urlparse(url)
            # url = parsed.geturl()
            # conn = self.poolmanager.connection_from_url(url)

        # return conn


    def add_headers(self, request):
        """
        Add headers to the request.

        This method is intended to be overridden by subclasses to inject
        custom headers. It does nothing by default.

        
        :param request: :class:`Request <Request>` to add headers to.
        """
        pass

    def build_proxy_headers(self, proxy):
        """Returns a dictionary of the headers to add to any request sent
        through a proxy. 

        :class:`HttpAdapter <HttpAdapter>`.

        :param proxy: The url of the proxy being used for this request.
        :rtype: dict
        """
        headers = {}
        #
        # TODO: build your authentication here
        #       username, password =...
        # we provide dummy auth here
        #
        username, password = ("user1", "password")

        if username:
            headers["Proxy-Authorization"] = (username, password)

        return headers