from distutils.log import debug
from enum import unique
from flask import Flask, jsonify, request, Response
from collections import defaultdict

app = Flask(__name__)


class NodeInfo:
    nodeCounter = 0
    def __init__(self, ip):
        self.ip = ip
        self.node_id = -1

    def updateNodeCounter(self):
        if self.node_id == -1:
            NodeInfo.nodeCounter += 1
            self.node_id = NodeInfo.nodeCounter

    def __hash__(self):
        return hash(self.ip)

    def __eq__(self, other): 
        return self.ip == other.ip

class ServerNodeInfo(NodeInfo):
    def __init__(self, ip, endpoint):
        super().__init__(ip)
        self.endpoint = endpoint

    def __hash__(self):
        return hash(self.ip + self.endpoint)

    def __eq__(self, other): 
        return self.ip == other.ip and self.endpoint == other.endpoint

    def __str__(self) -> str:
        return 'Server'

    def detailInfo(self) -> str:
        return f'Endpoint: {self.endpoint}'

class ClientNodeInfo(NodeInfo):
    def __init__(self, ip, agent):
        super().__init__(ip)
        self.agent = agent

    def __hash__(self):
        return hash(self.ip + self.agent)

    def __eq__(self, other): 
        return self.ip == other.ip and self.agent == other.agent

    def __str__(self) -> str:
        return 'Client'

    def detailInfo(self) -> str:
        return f'Agent: {self.agent}'

class EdgeInfo:
    edgeCounter = 0
    def __init__(self, node_a_id, node_b_id, detail):
        self.node_a_id = node_a_id
        self.node_b_id = node_b_id
        self.edge_id = -1
        self.edge_detail = detail

    def updateEdgeCounter(self):
        if self.edge_id == -1:
            EdgeInfo.edgeCounter += 1
            self.edge_id = EdgeInfo.edgeCounter

    def __hash__(self):
        return hash(self.node_a_id + self.node_b_id)

    def __eq__(self, other):
        return self.node_a_id == other.node_a_id and self.node_b_id == other.node_b_id

# Counter for Responses
IpNodeTotalRespDict = defaultdict(int)
IpNodeTotalSuccessRespDict = defaultdict(int)

# Graph related sets
NodeDict = dict()
EdgeSet = set()

# Route for incoming Stream data
@app.route('/cribl', methods = ['POST', 'PUT'])
def update_cribl():
    if  request.content_type != "application/json":
            return Response(
                response="Incorrect content format, require JSON", status=400
            )
    request_data_list = request.get_json()
    for event in request_data_list:
        if event.get('source') == 'http.resp':
        
            # app.logger.info(f'Event received {event}')

            event_data = event.get('data')
            target_ip = event_data.get("net_host_ip")
            source_ip = event_data.get("net_peer_ip")
            http_user_agent = event_data.get("http_user_agent", "")
            http_target = event_data.get("http_target", "")
            status_code = event_data.get("http_status_code")
            http_scheme = event_data.get("http_scheme")

            client_node = ClientNodeInfo(source_ip, http_user_agent)
            if client_node not in NodeDict:
                client_node.updateNodeCounter()
                NodeDict[client_node] = client_node.node_id

            client_id = NodeDict[client_node]
                
            server_node = ServerNodeInfo(target_ip, http_target)
            if server_node not in NodeDict:
                server_node.updateNodeCounter()
                NodeDict[server_node] = server_node.node_id

            server_id = NodeDict[server_node]

            edge = EdgeInfo(client_id, server_id, http_scheme)
            if edge not in EdgeSet:
                edge.updateEdgeCounter()
                EdgeSet.add(edge)
        
            # Handle responsesNo
            IpNodeTotalRespDict[client_node] += 1
            if 200 <= status_code <= 299:
                IpNodeTotalSuccessRespDict[client_node] += 1

    return jsonify(status= "Update OK")


@app.route('/api/graph/fields')
def fetch_graph_fields():
    app.logger.info("fetch_graph_fiels")

    nodes_fields = [{"field_name": "id", "type": "string"},
                    {"field_name": "title", "type": "string", "displayName": "Ip Address"},
                    {"field_name": "subTitle", "type": "string", "displayName": "-"},
                    {"field_name": "mainStat", "type": "string", "color": "blue", "displayName": "Total no of HTTP Request"},
                    {"field_name": "secondaryStat", "type": "string", "color": "yellow", "displayName": ""},
                    {"field_name": "arc__failed", "type": "number", "color": "red", "displayName": "Failed"},
                    {"field_name": "arc__passed", "type": "number", "color": "green", "displayName": "Passed"},
                    {"field_name": "detail__role", "type": "string", "displayName": "Role"}]
    edges_fields = [
        {"field_name": "id", "type": "string"},
        {"field_name": "source", "type": "string"},
        {"field_name": "target", "type": "string"},
        {"field_name": "mainStat", "type": "string"},
    ]
    result = {"nodes_fields": nodes_fields,
              "edges_fields": edges_fields}
    return jsonify(result)


# query=timeseries
@app.route('/api/graph/data')
def fetch_graph_data():
# Query
    # Path no query
    app.logger.info(f"fetch_graph_data")
    nodes =[]

    for Nodeobj in NodeDict.keys():
        TotalResponse = IpNodeTotalRespDict.get(Nodeobj,0)

        if TotalResponse != 0:
            SuccessResponse = IpNodeTotalSuccessRespDict.get(Nodeobj,0)
            # Normalize to 1
            SuccessNormalize = float(SuccessResponse)/float(TotalResponse)
            FailedNormalize = 1 - SuccessNormalize
        else:
            # No reponse yet ??
            SuccessNormalize = 1
            FailedNormalize = 0

        TotalResponseStr = "" if TotalResponse == 0 else f'{TotalResponse} Requests'
        SecondaryStat = Nodeobj.detailInfo()
        DetailedRole = str(Nodeobj)

        nodes.append({ "id": f'{Nodeobj.node_id}',
                            "title": Nodeobj.ip,
                            "subTitle": f'Node {Nodeobj.node_id}',
                            "detail__role": DetailedRole,
                            "arc__failed": FailedNormalize,
                            "arc__passed": SuccessNormalize,
                            "mainStat": TotalResponseStr,
                            "secondaryStat": SecondaryStat})

        app.logger.info(f'{nodes}')

    edges = []

    for EdgeDb in EdgeSet:
        edges.append({ "id": f'{EdgeDb.edge_id}',
                        "source": f'{EdgeDb.node_a_id}',
                        "target": f'{EdgeDb.node_b_id}',
                        "mainStat": f'{EdgeDb.edge_detail}'})

    result = {"nodes": nodes, "edges": edges}
    return jsonify(result)


@app.route('/api/health')
def check_health():
    return "API is working well!"


app.run(host='0.0.0.0', port=5000, debug=True)