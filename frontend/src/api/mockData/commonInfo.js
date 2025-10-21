export default {
    getMenuData: () => {
        return {
            code: 200,
            data: [
                {
                    path: '/home',
                    label: '首页',
                    icon: 'house'
                },
                {
                    path: '/',
                    label: '环境',
                    icon: 'location',
                    children: [
                        {
                            path: '/env/info',
                            label: '环境信息',
                            icon: 'setting'
                        },
                        {
                            path: '/env/version',
                            label: '组件版本',
                            icon: 'setting'
                        },
                        {
                            path: '/env/compare',
                            label: '版本比较',
                            icon: 'setting'
                        }
                    ]
                },
                {
                    path: '/user',
                    label: '用户管理1',
                    icon: 'user'
                }
            ],
            msg: "success"
        }
    }
}



