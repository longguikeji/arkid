import {UserAction} from './actions/user'
import {Page, launch} from 'puppeteer';
import {appSearchAction} from './actions/appSearch';
import {organizationAction} from './actions/organization';
import {setAction} from './actions/setting';
import {accountAction} from './actions/account';
import cofig from './config';
import expectPuppeteer = require('expect-puppeteer');
import { appMessageAction } from './actions/appMessage';



describe('一账通-登录测试', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');

    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证登录跳转链接' , async() => {
        const url = await page.url();
        await expect(url).toBe('https://arkid.demo.longguikeji.com/#/workspace/apps');
    },30000);

    test('TEST_002:验证标题' , async() => {
        const pageTitle = await page.$eval('title', elem => {
            return elem.innerHTML;
        });
        await expect(pageTitle).toEqual('ArkID');
    },30000);


})

describe('一账通-我的应用信息测试', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');
  
        let appmessageaction = new appMessageAction();
        await appmessageaction.appinformation(page);
        
    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证我的应用页面应用数量' , async() => {
        const appsNum = await page.$$('.card-list.flex-row').children("li").length;
        await expect(appsNum).toEqual('3');
    },30000);

    test('TEST_002:验证我的应用页面应用名称' , async() => {
        const appName1 = await page.$eval('.card-list.flex-row>li:first-child .name', elem => {
            return elem.innerHTML;
        });
        await expect(appName1).toEqual('百度');

        const appName2 = await page.$eval('.card-list.flex-row>li:nth-child(2) .name', elem => {
            return elem.innerHTML;
        });
        await expect(appName2).toEqual('街道OA');

        const appName3 = await page.$eval('.card-list.flex-row>li:last-child .name', elem => {
            return elem.innerHTML;
        });
        await expect(appName3).toEqual('啦啦啦');

    },30000);

    test('TEST_002:验证我的应用页面应用备注' , async() => {
        const appPs1 = await page.$eval('.card-list.flex-row>li:first-child .intro', elem => {
            return elem.innerHTML;
        });
        await expect(appPs1).toEqual('百度111');

        const appPs2 = await page.$eval('.card-list.flex-row>li:nth-child(2) .intro', elem => {
            return elem.innerHTML;
        });
        await expect(appPs2).toBeNull();

        const appPs3 = await page.$eval('.card-list.flex-row>li:last-child .intro', elem => {
            return elem.innerHTML;
        });
        await expect(appPs3).toEqual('哈哈哈');


    },30000);

})

describe('一账通-我的应用搜索框测试', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');
  
        let appsearchaction = new appSearchAction();
        await appsearchaction.appinformation(page, '街道');
        
    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证我的应用页面搜索框' , async() => {
        const appName = await page.$eval('.ws-apps--app-box.flex-col .name', elem => {
            return elem.innerHTML;
        });
        await expect(appName).toEqual('街道OA');
    },30000);

})

describe('一账通-通讯录测试', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');

        let organizationaction = new organizationAction();
        await organizationaction.origanization(page);
        
    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证通讯录页面链接' , async() => {
        const url = await page.url();
        await expect(url).toBe('https://arkid.demo.longguikeji.com/#/workspace/contacts');
    },30000);



})

describe('一账通-个人资料测试', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');

        let setaction = new setAction();
        await setaction.setting(page);
        
    },30000)
    afterEach ( async () => {
        await page.close();
    })


    test('TEST_001:验证个人资料页面链接' , async() => {
        const url = await page.url();
        await expect(url).toBe('https://arkid.demo.longguikeji.com/#/workspace/userinfo');
    },30000);

    test('TEST_002:验证个人资料页面添加手机号' , async() => {
        const addMobileBtn = await page.waitForSelector('.mobile .ivu-btn.ivu-btn-default');
         await addMobileBtn.click();

        const phoneTitle1 = await page.$eval('.ui-workspace-userinfo-verify-password .title', elem => {
            return elem.innerHTML;
        });
        await expect(phoneTitle1).toEqual('修改个人邮箱/手机号需要验证密码');

        const pwdInput = await page.waitForSelector('input[placeholder="输入密码"]');
        await pwdInput.type("longguikeji");

        const phoneBtn = await page.waitForSelector('.ivu-btn.ivu-btn-primary.ivu-btn-large');
        await phoneBtn.click();

        const phoneTitle2 = await page.$eval('.ui-workspace-userinfo-reset-mobile .title', elem => {
            return elem.innerHTML;
        });
        await expect(phoneTitle2).toEqual('修改手机号');

    },30000);

    test('TEST_003:验证个人资料页面添加邮箱' , async() => {
        const addEmailBtn = await page.waitForSelector('.email .ivu-btn.ivu-btn-default');
         await addEmailBtn.click();

        const emailTitle1 = await page.$eval('.ui-workspace-userinfo-verify-password .title', elem => {
            return elem.innerHTML;
        });
        await expect(emailTitle1).toEqual('修改个人邮箱/手机号需要验证密码');

        const pwdInput = await page.waitForSelector('input[placeholder="输入密码"]');
        await pwdInput.type("longguikeji");

        const emailBtn = await page.waitForSelector('.ivu-btn.ivu-btn-primary.ivu-btn-large');
        await emailBtn.click();

        const emailTitle2 = await page.$eval('.ui-workspace-userinfo-reset-email .title', elem => {
            return elem.innerHTML;
        });
        await expect(emailTitle2).toEqual('修改个人邮箱');

    },30000);


    test('TEST_004:验证个人资料页面修改姓名' , async() => {
        const nameInput = await page.waitForSelector('input[placeholder="请输入 姓名"]');
        await nameInput.type("abc");

        const saveBtn = await page.waitForSelector('.flex-row.flex-auto .ivu-btn.ivu-btn-primary');
         await saveBtn.click();

        const personName1 = await page.$eval('.ui-workspace-userinfo--summary h4', elem => {
            return elem.innerHTML;
        });
        await expect(personName1).toEqual('abc');

        const personName2 = await page.$eval('.ui-user-info li[data-label="姓名"]', elem => {
            return elem.innerHTML;
        });
        await expect(personName2).toEqual('abc');

    },30000);



})






/*async function run(){
    let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
    let page:Page = await browser.newPage();
    let useraction = new UserAction();
    let deskaction = new deskAction();
    let organizationaction = new organizationAction();
    let setaction = new setAction();
    let accountaction = new accountAction(); 
    

    await useraction.login(page, 'admin', 'longguikeji');

    await page.goto('https://arkid.demo.longguikeji.com/#/workspace/apps');

    await deskaction.appinformation(page, '街道');

    await organizationaction.origanization(page, "111");

    await setaction.setting(page, "abc");

    await accountaction.addAccount(page, "meixinyue", "meixinyue", "mei123456", "mei123456", "15822186268", "1821788073@qq.com", "meixinyue11@163.com", "zxzx");

    await accountaction.setAccount(page, "123456", "123456", "LTAIOWvU6MD0np72", "123456", "SMS_158010015", "aaaa");

    await accountaction.synchroAccount(page, "123456", "123456", "123456", "123456");



}

run();*/