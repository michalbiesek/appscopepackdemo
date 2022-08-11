from distutils.log import debug
from flask import Flask, jsonify, request, Response
from collections import defaultdict

app = Flask(__name__)

# Contains the hashmpa source IP and which IP was accessed
SourceIpDestIpDict = defaultdict(set)
# Contains mapping IP -> Node Id
IpNodeIdDict = dict()
# Counter for Http Request
IpNodeTotalReqDict = defaultdict(int)
# Counter for Http Responses
IpNodeTotalRespDict = defaultdict(int)
# Counter for Http Success Responses
IpNodeTotalSuccessRespDict = defaultdict(int)
IpSourceDestEdgeIdDict =  dict()
Node_id = 1
Edge_id = 1

# Route for incoming Stream data
@app.route('/cribl', methods = ['POST', 'PUT'])
def update_cribl():
    global Node_id
    global Edge_id

    if  request.content_type != "application/json":
            return Response(
                response="Incorrect content format, require JSON", status=400
            )
    request_data_list = request.get_json()
    for event in request_data_list:
        app.logger.info(f'Event received {event}')
        source = event.get('source')

        event_data = event.get('data')
        # host = event.get('host')
        target_ip = event_data.get("net_host_ip")
        source_ip = event_data.get("net_peer_ip")

        SourceIpDestIpDict[source_ip].add(target_ip)

        # relation between source and target
        hash_value = hash(source_ip + target_ip)
        if hash_value not in IpSourceDestEdgeIdDict:
            IpSourceDestEdgeIdDict[hash_value] = Edge_id
            Edge_id += 1
        if source == 'http.resp':
            IpNodeTotalRespDict[source_ip] +=1
            status_code = event_data.get("http_status_code")
            if 200 <= status_code <= 299:
                IpNodeTotalSuccessRespDict[source_ip] += 1
        elif source == 'http.req':
            IpNodeTotalReqDict[source_ip] +=1

        # app.logger.info("host_ip %s peer_ip %s source %s host %s", host_ip, peer_ip, source, host)
        if target_ip not in IpNodeIdDict:
            IpNodeIdDict[target_ip] = Node_id
            Node_id += 1
        if source_ip not in IpNodeIdDict:
            IpNodeIdDict[source_ip] = Node_id
            Node_id += 1

    return jsonify(status= "POST OK", id= 1000)


@app.route('/api/graph/fields')
def fetch_graph_fields():
    app.logger.info("fetch_graph_fiels")

    nodes_fields = [{"field_name": "id", "type": "string"},
                    {"field_name": "title", "type": "string", "displayName": "Ip Address"},
                    {"field_name": "subTitle", "type": "string", "displayName": "Port"},
                    {"field_name": "mainStat", "type": "number", "color": "blue", "displayName": "Requests"},
                    {"field_name": "secondaryStat", "type": "number", "color": "yellow", "displayName": "Responses"},
                    {"field_name": "arc__failed", "type": "number", "color": "red", "displayName": "Failed"},
                    {"field_name": "arc__passed", "type": "number", "color": "green", "displayName": "Passed"},
                    {"field_name": "detail__role", "type": "string", "displayName": "HostName"}]
    edges_fields = [
        {"field_name": "id", "type": "string"},
        {"field_name": "source", "type": "string"},
        {"field_name": "target", "type": "string"},
        {"field_name": "mainStat", "type": "string"},
    ]
    result = {"nodes_fields": nodes_fields,
              "edges_fields": edges_fields}
    return jsonify(result)


@app.route('/api/graph/data')
def fetch_graph_data():
# Query


    # Path no query
    app.logger.info("fetch_graph_data")
    nodes =[]
    for k, v in (IpNodeIdDict.items()):
        TotalResponse = IpNodeTotalRespDict.get(k,0)
        if TotalResponse != 0:
            SuccessResponse = IpNodeTotalSuccessRespDict.get(k,0)
            # Normalize to 1
            SuccessNormalize = float(SuccessResponse)/float(TotalResponse)
            FailedNormalize = 1 - SuccessNormalize
        else:
            # No reponse yet ??
            SuccessNormalize = 1
            FailedNormalize = 0
        nodes.append({ "id": f'{v}',
                            "title": k,
                            "subTitle": f'Node {v}',
                            "detail__role": "foo",
                            "arc__failed": FailedNormalize,
                            "arc__passed": SuccessNormalize,
                            "mainStat": IpNodeTotalReqDict.get(k,0),
                            "secondaryStat": TotalResponse})
        # app.logger.info(f'id {v}, title {k}')

    # edge_id = 1
    edges = []
    for source_ip, dest_ip_list in (SourceIpDestIpDict.items()):
        for dest_ip in dest_ip_list :
            hash_value = hash(source_ip + dest_ip)
            edge_id = IpSourceDestEdgeIdDict.get(hash_value)
            edges.append({ "id": f'{edge_id}',
                                "source": f'{IpNodeIdDict.get(source_ip)}',
                                "target": f'{IpNodeIdDict.get(dest_ip)}',
                                "mainStat": f'Foo Relation'})
            # edge_id += 1
            # app.logger.info(f'edge id {edge_id} source {Node_SetIP.get(k)} dest {Node_SetIP.get(single_dest)}')

    result = {"nodes": nodes, "edges": edges}
    return jsonify(result)


@app.route('/api/health')
def check_health():
    return "API is working well!"


app.run(host='0.0.0.0', port=5000, debug=True)