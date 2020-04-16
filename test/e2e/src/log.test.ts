import { UserAction } from './actions/user';
import {Page, launch} from 'puppeteer';
import config from './config';
import expectPuppeteer = require('expect-puppeteer');

declare var global: any

describe('一账通-测试操作日志', () => {
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

    },50000)
    afterAll ( async () => {
       // await page.close();
    })

    test('TEST_001:验证操作日志' , async() => {
        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        console.log(page.url());

        const logBtn = await page.waitForSelector('.header-middle a[href="#/admin/oplog"]');
        await logBtn.click();

        await page.waitFor(2000);
 
        const loginLog = await page.$eval('.ivu-table-tbody>tr>td>div>div', elem => {
            return elem.innerHTML;
        });
        await expect(loginLog).toEqual('登录');

        const loginLogPer = await page.$eval('.ivu-table-tbody>tr>td:nth-child(2)>div>div', elem => {
            return elem.innerHTML;
        });
        await expect(loginLogPer).toEqual('ad');

    },30000);

    test('TEST_002:验证查看详细日志' , async() => {
       // const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        //await manageBtn.click();

        console.log(page.url());

        const logBtn = await page.waitForSelector('.header-middle a[href="#/admin/oplog"]');
        await logBtn.click();

        await page.waitFor(2000);

        const logDetailsBtn = await page.waitForSelector('.ivu-table-tbody>tr>td:last-child>div');
        await logDetailsBtn.click();
        
        await page.waitFor(2000);

        const loginLog = await page.$eval('div.ivu-modal-body > div > div.left > div.basic > div:nth-child(1) > span.content', elem => {
            return elem.innerHTML;
        });
        await expect(loginLog).toEqual('登录');

        const loginLogPer = await page.$eval('div.ivu-modal-body > div > div.left > div.basic > div:nth-child(2) > span.content', elem => {
            return elem.innerHTML;
        });
        await expect(loginLogPer).toEqual('ad');

    },30000);

})
