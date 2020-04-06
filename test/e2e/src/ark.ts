
// import {Page, launch} from 'puppeteer';

// import config from './config';
// import expectPuppeteer = require('expect-puppeteer');


// const puppeteer = require('puppeteer');
// test('TEST_001:验证标题', async () => {
//     const browser = await puppeteer.launch({headless:false});
//     const page = await browser.newPage();
//     await page.goto('http://192.168.200.115:8989','10000');
//     const title = await page.title();
//     expect(title).toBe('ArkID');
//     await browser.close();
//     },60000);


//     test('TEST_002:验证登录跳转链接' , async() => {
//         const browser = await puppeteer.launch({headless:false});
//         const page = await browser.newPage();
//         await page.goto('http://192.168.200.115:8989','10000');

//         const usernameInput = await page.waitForSelector('input[type = "text"]');
//         await usernameInput.type("admin");
        
//         const passwordInput = await page.waitForSelector('input[type = "password"]');
//         await passwordInput.type("admin");

//         const loginBtn = await page.waitForSelector('button[type = "button"]');
//         await loginBtn.click();

//         await page.waitFor(6000);

//         const url = await page.url();
//         await expect(url).toContain('http://192.168.200.115:8989/#/workspace/apps');

//         await browser.close();
//     },30000);

//     // test('TEST_001:验证退出链接' , async() => {
//     //     const browser = await puppeteer.launch({headless:false});
//     //     const page = await browser.newPage();
//     //     await page.goto('http://192.168.200.115:8989','10000');

//     //     const usernameInput = await page.waitForSelector('input[type = "text"]');
//     //     await usernameInput.type("admin");
        
//     //     const passwordInput = await page.waitForSelector('input[type = "password"]');
//     //     await passwordInput.type("admin");

//     //     const loginBtn = await page.waitForSelector('button[type = "button"]');
//     //     await loginBtn.click();

//     //     await page.waitFor(6000);

//     //     const settingBtn = await page.waitForSelector('.ivu-icon.ivu-icon-md-arrow-dropdown');
//     //     await settingBtn.click();

//     //     const exitBtn = await page.waitForSelector('.ivu-dropdown-menu>li');
//     //     await exitBtn.click();

//     //     const url = await page.url();
//     //     await expect(url).toContain('https://192.168.200.115:8989/');
//     // },30000);



//     test('TEST_001:验证我的应用页面应用数量' , async() => {
//         const browser = await puppeteer.launch({headless:false});
//         const page = await browser.newPage();
//         await page.goto('http://192.168.200.115:8989','10000');

//         const usernameInput = await page.waitForSelector('input[type = "text"]');
//         await usernameInput.type("admin");
        
//         const passwordInput = await page.waitForSelector('input[type = "password"]');
//         await passwordInput.type("admin");

//         const loginBtn = await page.waitForSelector('button[type = "button"]');
//         await loginBtn.click();

//         const appName1 = await page.$eval('.card-list.flex-row>li:first-child .name', (el: { innerHTML: any; }) => {
//             return el.innerHTML;
//         });
//         await expect(appName1).toEqual('猎聘');

//         const appName2 = await page.$eval('.card-list.flex-row>li:nth-child(2) .name', (elem: { innerHTML: any; }) => {
//             return elem.innerHTML;
//         });
//         await expect(appName2).toEqual('测试应用');

//         const appName3 = await page.$eval('.card-list.flex-row>li:last-child .name', (elem: { innerHTML: any; }) => {
//             return elem.innerHTML;
//         });
//         await expect(appName3).toEqual('百度');
        
//         await browser.close();
//     },30000);