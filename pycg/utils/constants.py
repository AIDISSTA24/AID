#
# Copyright (c) 2020 Vitalis Salis.
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
RETURN_NAME = "<RETURN>"
LAMBDA_NAME = "<LAMBDA_{}>"  # needs to be formatted
BUILTIN_NAME = "<builtin>"
EXT_NAME = "<external>"

FUN_DEF = "FUNCTIONDEF"
NAME_DEF = "NAMEDEF"
MOD_DEF = "MODULEDEF"
CLS_DEF = "CLASSDEF"
EXT_DEF = "EXTERNALDEF"

OBJECT_BASE = "object"

CLS_INIT = "__init__"
ITER_METHOD = "__iter__"
NEXT_METHOD = "__next__"
STATIC_METHOD = "staticmethod"

INVALID_NAME = "<**INVALID**>"

CALL_GRAPH_OP = "call-graph"
KEY_ERR_OP = "key-error"


NETWORK_PROTOCOL_METHODS_LIST = ["socket.socket",
                                 
                                 "requests.Session", "requests.get", "requests.session.put", "requests.post", "requests.Session.send", "requests.Session.get", "requests.request", "requests.Session.headers.update",

                                 "requests_oauthlib.OAuth2Session.refresh_token", 

                                 "aiohttp.ClientSession.get", "aiohttp.ClientSession.request", "aiohttp.ClientSession", "aiohttp.ClientTimeout", "aiohttp.ClientSession.post", "aiohttp.client.ClientSession.request", "aiohttp.ClientResponse.text",

                                 "asyncio.open_connection", "asyncio.get_event_loop.create_datagram_endpoint", "asyncio.StreamWriter.write", "asyncio.DatagramTransport.sendto", "asyncio.BaseTransport.write",

                                 "httpx.AsyncClient", "httpx.AsyncClient.post", "httpx.AsyncClient.get",

                                 "urllib.request.Request",

                                 "bleak_retry_connector.establish_connection.write_gatt_char",

                                 "paho.mqtt.client.Client.publish",

                                 "btle.Peripheral",

                                 "pyserial.Serial",

                                 "aiocoap.Message",

                                 "websockets.client.connect",
                                 ]