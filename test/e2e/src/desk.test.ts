import { UserAction } from './actions/user';
import {Page, launch} from 'puppeteer';
import {appSearchAction} from './actions/appSearch';
import {organizationAction} from './actions/organization';
import {setAction} from './actions/setting';
import config from './config';
import expectPuppeteer = require('expect-puppeteer');
import { appMessageAction } from './actions/appMessage';

declare var global: any

describe('一账通-登录测试', () => {
    let page : Page;

    beforeAll( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

    },80000)

    afterAll ( async () => {

    })

    test('TEST_001:验证标题' , async() => {
        const pageTitle = await page.$eval('title', elem => {
            return elem.innerHTML;
        });
        await expect(pageTitle).toEqual('ArkID');
        
    },30000);

    test('TEST_002:验证登录跳转链接' , async() => {

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        const url = await page.url();
        await expect(url).toMatch('#/workspace/apps');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    },50000);
})

describe('一账通-我的应用信息测试', () => {
    let page : Page;
    
    beforeAll( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');
        
    },120000)
    afterAll ( async () => {
       // await page.close();
    })
    
    test('TEST_001:验证我的应用页面应用名称' , async() => {
        let appmessageaction = new appMessageAction();
        await appmessageaction.appinformation(page);

        const appName1 = await page.$eval('.card-list.flex-row>li:first-child .name', elem => {
            return elem.innerHTML;
        });
        await expect(appName1).toEqual('猎聘');

        const appName2 = await page.$eval('.card-list.flex-row>li:nth-child(2) .name', elem => {
            return elem.innerHTML;
        });
        await expect(appName2).toEqual('测试应用');

        const appName3 = await page.$eval('.card-list.flex-row>li:last-child .name', elem => {
            return elem.innerHTML;
        });
        await expect(appName3).toEqual('百度');

    },30000);

    test('TEST_002:验证我的应用页面应用备注' , async() => {
        const appPs1 = await page.$eval('.card-list.flex-row>li:first-child .intro', elem => {
            return elem.innerHTML;
        });
        await expect(appPs1).toBe("");

        const appPs2 = await page.$eval('.card-list.flex-row>li:nth-child(2) .intro', elem => {
            return elem.innerHTML;
        });
        await expect(appPs2).toBe("");

        const appPs3 = await page.$eval('.card-list.flex-row>li:last-child .intro', elem => {
            return elem.innerHTML;
        });
        await expect(appPs3).toEqual('百度搜索');

    },30000);

    test('TEST_003:验证我的应用页面搜索框' , async() => {

        let appsearchaction = new appSearchAction();
        await appsearchaction.appinformation(page, 'bing');

        const appName = await page.$eval('.ws-apps--app-box.flex-col .name', elem => {
            return elem.innerHTML;
        });
        await expect(appName).toEqual('bing test');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    },60000);

})

describe('一账通-通讯录测试', () => {
    let page : Page;
    
    beforeAll( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let organizationaction = new organizationAction();
        await organizationaction.origanization(page);
        
    },150000)
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证通讯录页面链接' , async() => {
        //await page.waitFor(2000);
        const url = await page.url();
        await expect(url).toMatch('workspace/contacts');
    },30000);

    test('TEST_002:验证通讯录页面的部门分类' , async() => {
        const departmentName1 = await page.$eval('.dept-list>li:first-child .name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(departmentName1).toEqual('部门一 (0人)');

        const departmentBtn1 = await page.waitForSelector('.dept-list>li:first-child');
        await departmentBtn1.click();

        const departmentName11 = await page.$eval('.dept-list .name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(departmentName11).toEqual('部门一1 (0人)');

        const departRetBtn1 = await page.waitForSelector('.path-name');
        await departRetBtn1.click();

        const departmentName2 = await page.$eval('.dept-list>li:nth-child(2) .name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(departmentName2).toEqual('部门二 (1人)');

        const departmentBtn2 = await page.waitForSelector('.dept-list>li:nth-child(2)');
        await departmentBtn2.click();

        const departmentName21 = await page.$eval('.user-list .flex-row .name', elem => {
            return elem.innerHTML;
        });
        await expect(departmentName21).toEqual('bumen2user');

        const departRetBtn2 = await page.waitForSelector('.path-name');
        await departRetBtn2.click();

        const departmentName3 = await page.$eval('.dept-list>li:last-child .name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(departmentName3).toEqual('部门三 (1人)');

        const departmentBtn3 = await page.waitForSelector('.dept-list>li:last-child');
        await departmentBtn3.click();

        const departmentName31 = await page.$eval('.flex-row .name', elem => {
            return elem.innerHTML;
        });
        await expect(departmentName31).toEqual('部门三1 (0人)');


        const departmentName32 = await page.$eval('.user-list .flex-row .name', elem => {
            return elem.innerHTML;
        });
        await expect(departmentName32).toEqual('bumen3user');
        
    },60000);

    test('TEST_004:验证通讯录页面自定义分类的项目组' , async() => {
        const departmentBtn = await page.waitForSelector('.ui-contact-page--side>li:last-child');
        await departmentBtn.click();

        await page.waitFor(2000);

        const departmentName1 = await page.$eval('.dept-list>li:first-child .name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(departmentName1).toEqual('A项目组 (1人)');

        const departmentBtn1 = await page.waitForSelector('.dept-list>li:first-child');
        await departmentBtn1.click();

        const departmentName11 = await page.$eval('.dept-list>li:first-child .name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(departmentName11).toEqual('分组一 (0人)');

        const userName11 = await page.$eval('.user-list .name', elem => {
            return elem.innerHTML;
        });
        await expect(userName11).toEqual('axiangmuzuuser');

        const departRetBtn1 = await page.waitForSelector('.path-name');
        await departRetBtn1.click();

        const departmentName2 = await page.$eval('.dept-list>li:nth-child(2) .name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(departmentName2).toEqual('B项目组 (1人)');

        const departmentBtn2 = await page.waitForSelector('.dept-list>li:nth-child(2)');
        await departmentBtn2.click();

        const departmentName21 = await page.$eval('.user-list .flex-row .name', elem => {
            return elem.innerHTML;
        });
        await expect(departmentName21).toEqual('bxiangmuzuuser');

        const departRetBtn2 = await page.waitForSelector('.path-name');
        await departRetBtn2.click();

        const departmentName3 = await page.$eval('.dept-list>li:last-child .name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(departmentName3).toEqual('C项目组 (1人)');

        const departmentBtn3 = await page.waitForSelector('.dept-list>li:last-child');
        await departmentBtn3.click();
        
        const departmentName31 = await page.$eval('.flex-row .name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(departmentName31).toEqual('C项目组分组 (0人)');

        const departmentName32 = await page.$eval('.user-list .flex-row .name', elem => {
            return elem.innerHTML;
        });
        await expect(departmentName32).toEqual('cxiangmuzuuser');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
        
    },50000);   

})

describe('一账通-个人资料测试', () => {
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');
        
    },130000)
    afterAll ( async () => {
        //await page.close();
    })


    test('TEST_001:验证个人资料页面链接' , async() => {
        let setaction = new setAction();
        await setaction.setting(page);

        const url = await page.url();
        await expect(url).toMatch('workspace/userinfo');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    },30000);

    test('TEST_002:验证个人资料页面添加手机号' , async() => {
        let setaction = new setAction();
        await setaction.setting(page);

        const addMobileBtn = await page.waitForSelector('.mobile .ivu-btn.ivu-btn-default');
         await addMobileBtn.click();

        const phoneTitle1 = await page.$eval('.ui-workspace-userinfo-verify-password .title', elem => {
            return elem.innerHTML;
        });
        await expect(phoneTitle1).toEqual('修改个人邮箱/手机号需要验证密码');

        const pwdInput = await page.waitForSelector('input[placeholder="输入密码"]');
        await pwdInput.type("admin");

        const phoneBtn = await page.waitForSelector('.ivu-btn.ivu-btn-primary.ivu-btn-large');
        await phoneBtn.click();

        await page.waitFor(3000);

        const phoneTitle2 = await page.$eval('.ui-workspace-userinfo-reset-mobile .title', elem => {
            return elem.innerHTML;
        });
        await expect(phoneTitle2).toEqual('修改手机号');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    },50000);

    test('TEST_003:验证个人资料页面添加邮箱' , async() => {
        let setaction = new setAction();
        await setaction.setting(page);

        const addEmailBtn = await page.waitForSelector('.email .ivu-btn.ivu-btn-default');
         await addEmailBtn.click();

        const emailTitle1 = await page.$eval('.ui-workspace-userinfo-verify-password .title', elem => {
            return elem.innerHTML;
        });
        await expect(emailTitle1).toEqual('修改个人邮箱/手机号需要验证密码');

        const pwdInput = await page.waitForSelector('input[placeholder="输入密码"]');
        await pwdInput.type("admin");

        const emailBtn = await page.waitForSelector('.ivu-btn.ivu-btn-primary.ivu-btn-large');
        await emailBtn.click();

        await page.waitFor(3000);

        const emailTitle2 = await page.$eval('.ui-workspace-userinfo-reset-email .title', elem => {
            return elem.innerHTML;
        });
        await expect(emailTitle2).toEqual('修改个人邮箱');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    },30000);

    test('TEST_004:验证个人资料页面修改姓名' , async() => {
        let setaction = new setAction();
        await setaction.setting(page);

        const nameInput = await page.waitForSelector('input[placeholder="请输入 姓名"]');
        await nameInput.type("111");

        const saveBtn = await page.waitForSelector('.flex-row.flex-auto .ivu-btn.ivu-btn-primary');
         await saveBtn.click();

        page = await global.browser.newPage()
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');
        const returnBtn = await page.waitForSelector('body > div.lg-layout > header > div.header-right > a:nth-child(1) > button');
        await returnBtn.click();

        const setBtn = await page.waitForSelector('a[href="#/workspace/userinfo"]');
        await setBtn.click();

        const personName1 = await page.$eval('.ui-workspace-userinfo--summary h4', elem => {
            return elem.innerHTML;
        });
        await expect(personName1).toEqual('ad111');

        const personName2 = await page.$eval('.ui-user-info li[data-label="姓名"]', elem => {
            return elem.innerHTML;
        });
        await expect(personName2).toEqual('ad111');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    },50000);

})
