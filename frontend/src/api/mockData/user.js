export default {
    getUserData: () => {
        return {
            code: 200,
            data: {
                data: [
                    {
                        id: 123,
                        name: '胡汉三',
                        role: "普通成员",
                        state: 1,
                        create_time: "2025.9.1 14.00",
                        last_time: "2025.9.1 14.00"
                    },
                    {
                        id: 123,
                        name: '胡汉三1',
                        role: "普通成员",
                        state: 1,
                        create_time: "2025.9.1 14.00",
                        last_time: "2025.9.1 14.00"
                    },
                    {
                        id: 123,
                        name: '胡汉三2',
                        role: "普通成员",
                        state: 1,
                        create_time: "2025.9.1 14.00",
                        last_time: "2025.9.1 14.00"
                    },

                ],
                total: 200
            },
            msg: "success"
        }
    }
}