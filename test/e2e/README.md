# 一账通UI自动化测试脚本环境搭建
本部分整合了 **TYPESCRIPT+PUPPETEER+JEST** 对一账通进行前端自动化测试。
### 一、typescript与jest安装配置    
1、mkdir arkid_test  //创建文件夹arkid_test         
2、cd arkid_test  <font color=green>//进入该文件夹</font>             
3、npm init   <font color=green>//初始化</font>            
4、安装需要的包
安装包         |命令
-----------------| ----------
TypeScript  | npm install typescript --save-dev
Jest               | npm install jest --save-dev
ts-jest     |npm install ts-jest --save-dev
@types/jest |npm install @types/jest --save-dev                                              

5、tsc --init  <font color=green>// 初始化相关配置文件，生成tsconfig.json</font>
tsconfig.json配置

```
{
  "compilerOptions": {
    "target": "es6",
    "module": "commonjs",
    "sourceMap": true,
    "outDir": "dist",
  }
}
```
6、jest --init  <font color=green>//初始化，生成jest.config.js</font>
jest.config.js配置
```
module.exports = {
  roots:[
    "<rootDir>"
  ],
  "moduleFileExtensions": [
    "ts",
    "js",
  ],
  "testMatch": [
    "**/*.test.*"
  ],    //匹配后缀包括.test.的ts和js文件
  "transform": {
    "^.+\\.ts$": "ts-jest"
  }
};
```
7、package.json配置
```
"scripts": {
    "test": "jest"
  }
```
### 二、puppeteer安装配置
1、安装依赖的安装包
|安装包         |命令|
|-----------------| ----------|
|puppeteer|npm install puppeteer --save-dev|
|@types/puppeteer|npm install @types/puppeteer --save-dev|
|@types/node|npm install @types/node --save-dev|
|@types/jest-environment-puppeteer|npm install @types/puppeteer --save-dev|
|jest-puppeteer|npm install jest-puppeteer --save-dev|
|jest-environment-puppeteer|npm install jest-environment-puppeteer --save-dev|
|expect-puppeteer|npm install expect-puppeteer --save-dev|
|@types/expect-puppeteer|npm install @types/expect-puppeteer --save-dev|


注：安装puppeteer会自动下载Chromium浏览器，Chromium无法下载时，可先下载淘宝镜像（` npm install -g cnpm --registry=https://registry.npm.taobao.org` ），使用cnpm下载puppeteer。
2、创建puppeteer_enviroment.js并配置
```
const PuppeteerEnviromenent = require('jest-environment-puppeteer');
class CustomEnvironmemnt extends PuppeteerEnviromenent {
    async setup() {
        await super.setup();
    }

    async teardown() {
        await super.teardown()
    }

}
module.exports = CustomEnvironmemnt
```
3、在jest.config.js里添加以下项                
（1）globalSetup：全部变量，再之前运行            
（2）globalTeardown：全部变量，再之后运行              
（3）testEnvironment：测试环境               
```
  "globalSetup": "jest-environment-puppeteer/setup",
  "globalTeardown": "jest-environment-puppeteer/teardown",
  "testEnvironment": "./puppeteer_enviroment.js",
```
### 三、运行
使用Visual Studio Code编辑器 New Terminal，输入npm run test即可。
