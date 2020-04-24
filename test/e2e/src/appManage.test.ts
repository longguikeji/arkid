import { UserAction } from './actions/user';
import {Page, launch} from 'puppeteer';
import {appSearchAction} from './actions/appSearch';
import {organizationAction} from './actions/organization';
import {setAction} from './actions/setting';
import {accountAction} from './actions/account';
import config from './config';
import expectPuppeteer = require('expect-puppeteer');
import {groupAction} from './actions/group';
import {configManageAction} from './actions/configManage';
import {appsManageAction} from './actions/appsManage';
import {managerSettingAction} from './actions/managerSetting';

declare var global: any

jest.setTimeout(600000);

describe('一账通-应用管理添加应用', () => {
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

    })
    afterAll ( async () => {

    })

    test('TEST_001:验证添加应用是否生效' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let appsmanageaction = new appsManageAction();
        await appsmanageaction.addApps(page, "携程", "https://www.ctrip.com/", "携程应用");

        await page.waitFor(3000);
        
        const appName = await page.$eval('.ivu-table-tbody>tr:first-child .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(appName).toEqual('携程');

        const mark = await page.$eval('.ivu-table-tbody>tr:first-child>td:nth-child(3) span', elem => {
            return elem.innerHTML;
        });
        await expect(mark).toEqual('携程应用');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    });

    test('TEST_002:验证添加应用在工作台是否生效' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        await page.waitFor(3000);
        const appName = await page.$eval('div.name-intro.flex-col.flex-auto > span.name', elem => {
            return elem.innerHTML;
        });
        await expect(appName).toEqual('携程');

        const mark = await page.$eval('div.name-intro.flex-col.flex-auto > span.intro', elem => {
            return elem.innerHTML;
        });
        await expect(mark).toEqual('携程应用');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    });

})

describe('一账通-应用管理编辑应用', () => {
    let page : Page;
    
    beforeEach( async () => {

        page = await global.browser.newPage()
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

    })
    afterEach ( async () => {
       // await page.close();
    })

    test('TEST_001:验证编辑应用是否生效' , async() => {

        let appsmanageaction = new appsManageAction();
        await appsmanageaction.editAppMassage(page, "111",  "111");

        const appName = await page.$eval('.ivu-table-tbody>tr:first-child .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(appName).toEqual('携程111');

        const mark = await page.$eval('.ivu-table-tbody>tr:first-child>td:nth-child(3) span', elem => {
            return elem.innerHTML;
        });
        await expect(mark).toEqual('携程应用111');
        await page.waitFor(3000);
        
        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    });

    test('TEST_002:验证编辑应用在工作台是否生效' , async() => {
       
        await page.waitFor(3000);
 
        const appName = await page.$eval('.card-list.flex-row>li:first-child .name-intro.flex-col.flex-auto .name', elem => {
            return elem.innerHTML;
        });
        await expect(appName).toEqual('携程111');

        const mark = await page.$eval('.card-list.flex-row>li:first-child .name-intro.flex-col.flex-auto .intro', elem => {
            return elem.innerHTML;
        });
        await expect(mark).toEqual('携程应用111');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    });

})

describe('一账通-应用管理删除应用', () => {
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');
        
    })
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证删除应用是否生效' , async() => {
        let appsmanageaction = new appsManageAction();
        await appsmanageaction.deleteApp(page);

        const appName = await page.$eval('.ivu-table-tbody>tr>td:nth-child(2) span', elem => {
            return elem.innerHTML;
        });
        await expect(appName).toEqual('猎聘');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    });

    test('TEST_002:验证删除应用在工作台是否生效' , async() => {

        await page.waitFor(3000);

        const appName = await page.$eval('.card-list.flex-row>li:first-child .name-intro.flex-col.flex-auto .name', elem => {
            return elem.innerHTML;
        });
        await expect(appName).toEqual('猎聘');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    });

})

describe('一账通-应用管理账号的权限', () => {
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

    })
    afterAll ( async () => {

    })

    test('TEST_001:验证账号的权限是否生效' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');
        
        let appsmanageaction = new appsManageAction();
        await appsmanageaction.userPower(page, "mei333");

        const resultNameBtn = await page.waitForSelector('.perm-results span');
        await resultNameBtn.click();

        await page.waitFor(2000);

        const resultName = await page.$eval('.ivu-modal-content .ivu-cell-group.name-list .ivu-cell-main .ivu-cell-title', elem => {
            return elem.innerHTML;
        });
        await expect(resultName).toEqual('mei333');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    });

    test('TEST_001:验证账号的权限是否生效' , async() => {

        let useraction = new UserAction();
        await useraction.login(page, 'mei333', 'mei333');
        
        const appName = await page.$eval('.flex-row .name', elem => {
            return elem.innerHTML;
        });
        await expect(appName).toEqual('猎聘');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    });

})

describe('一账通-应用管理部门的权限', () => {
    let page : Page;
    
    beforeAll( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');
        let appsmanageaction = new appsManageAction();
        await appsmanageaction.departmentPower(page, "部门三");

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    })
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证部门的权限是否生效' , async() => {    
        page = await global.browser.newPage()
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'bumen3user', 'bumen3user');

        const appName = await page.$eval('.flex-row .name', elem => {
            return elem.innerHTML;
        });
        await expect(appName).toEqual('猎聘');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    });

})
