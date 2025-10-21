import Mock from 'mockjs'
import envInfo from './mockData/envInfo';
import commonInfo from './mockData/commonInfo';
import user from './mockData/user';
// 参数1 拦截的路径 参数2 拦截请求方法 参数3，制造的假数据
Mock.mock(
    /api\/env\/getEnvData/,
    "get",
    envInfo.getEnvData
);
Mock.mock(
    /api\/user\/get_menu/,
    "get",
    commonInfo.getMenuData
);
Mock.mock(
    /api\/user\/info/,
    "get",
    user.getUserData
);
Mock.mock(
    /api\/env\/projects/,
    "get",
    envInfo.getProjectName
);
