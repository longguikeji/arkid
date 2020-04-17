import { UserAction } from './actions/user';
import {Page, launch} from 'puppeteer';
import {appSearchAction} from './actions/appSearch';
import config from './config';
import expectPuppeteer = require('expect-puppeteer');

declare var global: any

describe('一账通-验证分组管理可见性', () => {
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

    },120000)
    afterAll ( async () => {
        await page.close();
    })

    test('TEST_001:验证分组管理分组可见性' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'mei111', 'mei111');

        console.log(page.url());
  
        await page.waitFor(2000);
       
       // await global.browser.disconnect();       
    },50000);

})

describe('一账通-验证分组管理可见性', () => {
    let page111 : Page;

    beforeAll( async () => {
        page111 = await global.browser.newPage()
        await page111.goto(config.url);

    },120000)
    afterAll ( async () => {
        //await page.close();
    })
test('TEST_001:验证分组管理分组可见性' , async() => {
        await page111.waitFor(3000);
        console.log("aaaaaaaaaa");
        console.log(page111.url());
      
        const usernameInput = await page111.waitForSelector('input[type = "text"]');
        await usernameInput.type("admin");
        const passwordInput = await page111.waitForSelector('input[type = "password"]');
        await passwordInput.type("admin");
        
        await page111.waitFor(2000);
        
        const loginBtn = await page111.waitForSelector('button[type = "button"]');
        await loginBtn.click();
        await page111.waitFor(2000);

        console.log(page111.url());



    },60000);
})
