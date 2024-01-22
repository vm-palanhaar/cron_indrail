import http.client, os, json

class ApiSetu_Train:

    def getTrainListApi(self) -> list[map]:
        print("(API) Initiating HTTPS Request")

        conn = http.client.HTTPSConnection("apigw.umangapp.in")

        payload = {
            'tkn' : os.getenv("TOKEN"),
            'lang' : "en",
            'usrid' : os.getenv("USER_ID"),
            'mode' : "web",
            'pltfrm' : "windows",
            'did' : None,
            'srvid' : os.getenv("INDRAIL_TRAINS_SRV_ID"),
            'deptid' : os.getenv("INDRAIL_TRAINS_DEPT_ID"),
            'subsid' : 0,
            'susid2' : 0,
            'formtrkr' : 0,
        }

        headers = {
            'Content-Type': "application/json",
            'Accept': "application/json",
            'deptid': os.getenv("INDRAIL_TRAINS_DEPT_ID"),
            'srvid': os.getenv("INDRAIL_TRAINS_SRV_ID"),
            'subsid': "0",
            'subsid2': "0",
            'formtrkr': "0",
            'x-api-key': os.getenv("API_KEY"),
        }
        
        conn.request("POST", "/CRISApi/ws1/nget/trainList", json.dumps(payload), headers)

        res = conn.getresponse()
        data = res.read()
        if res.status == 200:
            print("(API) Train List API response success")
        else:
            print(f"(API) Train List API response status code: {res.status}")
            print(data.decode())
            return
        conn.close()

        try:
            json_data = json.loads(data.decode())
        except json.JSONDecodeError as e:
            print(f'(API) Error decoding JSON: {e}')

        print(f"(API) Total no. of train: {len(json_data['pd']['trainList'])}")

        train_list = []
        for t in json_data['pd']['trainList']:
            train = [temp.strip() for temp in t.split("-")]
            train_list.append({
                "trainNo" : train[0],
                "trainName" : train[1]
            })
        return train_list
    