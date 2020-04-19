import { UserAction } from './actions/user';
import {Page, launch} from 'puppeteer';
import config from './config';
import expectPuppeteer = require('expect-puppeteer');
import {configManageAction} from './actions/configManage';


declare var global: any

describe('一账通-配置管理登录页面', () => {
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);      

    },90000)
    afterAll ( async () => {
        //await page.close();
    })
    
    test('TEST_001:验证配置管理页面链接' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        await page.waitFor(1000);

        const configManageBtn = await page.waitForSelector('body > div.lg-layout > header > div.header-middle > ul > a:nth-child(4)');
        await configManageBtn.click();

        await page.waitFor(2000);

        const url = await page.url();
        await expect(url).toMatch('#/admin/config');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
        
    },30000);

    test('TEST_002:验证修改公司面名称是否生效' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let configmanageaction = new configManageAction();
        await configmanageaction.loginSetting(page,"北京龙归科技");
        
        const companyName = await page.$eval('.org-name', elem => {
            return elem.innerHTML;
        });
        await expect(companyName).toEqual('北京龙归科技');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
        
    },30000);

    test('TEST_003:验证配置管理页面"去进行账号配置"链接' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let configmanageaction = new configManageAction();
        await configmanageaction.urlTest(page);

        const url = await page.url();
        await expect(url).toMatch('#/admin/account/settings');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
        
    },30000);

})
