export default {
    getEnvData: () => {
        return {
                "code": 200,
                "msg": "success",
                "data": {
                    "total": 2,
                    "page": 1,
                    "size": 10,
                    "envs": [
                            {
                                "id": 1,
                                "name": "dev",
                                "domain": "https://dev.example.com/",
                                "need_version": true,
                                "desc": "开发环境",
                                "created_at": "2023-10-01 10:30:00",
                                "updated_at": "2023-10-01 10:30:00",
                                "user": {
                                        "id": 1,
                                        "username": "admin"
                                        },
                                "project": {
                                        "id": 1,
                                        "name": "MyProject"
                                        }
                            },
                            {
                                "id": 2,
                                "name": "test",
                                "domain": "https://test.example.com/",
                                "need_version": false,
                                "desc": "测试环境",
                                "created_at": "2023-10-02 14:15:00",
                                "updated_at": "2023-10-02 14:15:00",
                                "user": {
                                        "id": 1,
                                        "username": "admin"
                                        },
                                "project": {
                                        "id": 1,
                                        "name": "MyProject"
                                        }
                            }
                    ]
                }
        }
    },
    getProjectName: ()=>{ 
        return {
            code: 200,
            data: [
                {id: 1, name: 'scnet', "desc": 'scnet'},
                {id: 2, name: 'gridview', "desc": ''},
                {id: 3, name: 'mix', "desc": ''},
            ],
            msg: "success"
        }
    }
    
}