const env = 'develop'
const EnvConfig = {
    prod: 'http://127.0.0.1:9998',
    develop: 'http://127.0.0.1:9998'
}

export default {
    env,
    baseUrl: EnvConfig[env]
}