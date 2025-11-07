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
                path: "ui-test",
                name: "ui-test",
                redirect: "/ui-test/test-users",
                children: [
                    {
                        path: "test-users",
                        name: "test-users",
                        component: () => import('@/views/UITest/TestUsers.vue'),
                    },
                    {
                        path: "elements",
                        name: "elements",
                        component: () => import('@/views/UITest/Elements.vue'),
                    },
                    {
                        path: "test-cases",
                        name: "test-cases",
                        component: () => import('@/views/UITest/TestCases.vue'),
                    },
                    {
                        path: "test-cases/new",
                        name: "test-case-new",
                        component: () => import('@/views/UITest/TestCaseDetail.vue'),
                    },
                    {
                        path: "test-cases/:id",
                        name: "test-case-view",
                        component: () => import('@/views/UITest/TestCaseDetail.vue'),
                    },
                    {
                        path: "test-cases/:id/edit",
                        name: "test-case-edit",
                        component: () => import('@/views/UITest/TestCaseDetail.vue'),
                    },
                    {
                        path: "test-suites",
                        name: "test-suites",
                        component: () => import('@/views/UITest/TestSuites.vue'),
                    },
                    {
                        path: "test-tasks",
                        name: "test-tasks",
                        component: () => import('@/views/UITest/TestTasks.vue'),
                    },
                    {
                        path: "test-reports",
                        name: "test-reports",
                        component: () => import('@/views/UITest/TestReports.vue'),
                    },
                    {
                        path: "test-reports/:id",
                        name: "test-report-detail",
                        component: () => import('@/views/UITest/TestReportDetail.vue'),
                    }
                ]
            },
            {
                path: "system",
                name: "system",
                redirect: "/system/user",
                children: [
                    {
                        path: "user",
                        name: "user",
                        component: () => import('@/views/User.vue'),
                    }
                ]
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