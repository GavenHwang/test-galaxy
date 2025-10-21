import {createRouter, createWebHashHistory} from 'vue-router'

const routes = [
    {
        path: '/',
        name: 'main',
        component: () => import('@/views/Main.vue'),
        redirect: "/home",
        children: [
            {
                path: "home",
                name: "home",
                component: () => import('@/views/Home.vue'),
            },
            {
                path: "env",
                name: "env",
                redirect: "/env/info", // 可选：添加默认重定向
                children: [
                    {
                        path: "info", // 移除了开头的 /
                        name: "info",
                        component: () => import('@/views/Env/EnvInfo.vue'),
                    },
                    {
                        path: "version", // 移除了开头的 /
                        name: "version",
                        component: () => import('@/views/Env/VersionInfo.vue'),
                    },
                    {
                        path: "compare", // 移除了开头的 /
                        name: "compare",
                        component: () => import('@/views/Env/Compare.vue'),
                    },
                    {
                        path: "detail/:id",
                        name: "detail",
                        component: () => import('@/views/Env/EnvDetail.vue'),
                    },
                    {
                        path: "history/:id", // 移除了开头的 /
                        name: "history",
                        component: () => import('@/views/Env/EnvHistory.vue'),
                    },
                ]
            },
            {
                path: "user",
                name: "user",
                component: () => import('@/views/User.vue'),
            }
        ]
    },
    {
        path: "/login",
        name: "login",
        component: () => import('@/views/Login.vue'),
    },
]

const router = createRouter({
    history: createWebHashHistory(),
    routes,
})

export default router