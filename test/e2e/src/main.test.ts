import { UserAction } from './actions/user';
import {Page, launch} from 'puppeteer';
import {appSearchAction} from './actions/appSearch';
import {organizationAction} from './actions/organization';
import {setAction} from './actions/setting';
import {accountAction} from './actions/account';
import config from './config';
import expectPuppeteer = require('expect-puppeteer');
import { appMessageAction } from './actions/appMessage';
import {groupAction} from './actions/group';
import {configManageAction} from './actions/configManage';
import {appsManageAction} from './actions/appsManage';
import {managerSettingAction} from './actions/managerSetting';

declare var global: any

describe('一账通-登录测试', () => {
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

    },30000)

    afterAll ( async () => {
        await page.close();
    })

    test('TEST_001:验证标题' , async() => {
        const pageTitle = await page.$eval('title', elem => {
            return elem.innerHTML;
        });
        await expect(pageTitle).toEqual('ArkID');

        await page.close();
    },30000);

    test('TEST_002:验证登录跳转链接' , async() => {

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        const url = await page.url();
        await expect(url).toMatch('#/workspace/apps');

    },40000);
})

describe('一账通-我的应用信息测试', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');
  
        let appmessageaction = new appMessageAction();
        await appmessageaction.appinformation(page);
        
    },30000)
    afterAll ( async () => {
        await page.close();
    })
    
    test('TEST_001:验证我的应用页面应用名称' , async() => {
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

})

describe('一账通-我的应用搜索框测试', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');
  
        let appsearchaction = new appSearchAction();
        await appsearchaction.appinformation(page, 'bing');
        
    },30000)
    afterAll ( async () => {
        await page.close();
    })

    test('TEST_001:验证我的应用页面搜索框' , async() => {
        const appName = await page.$eval('.ws-apps--app-box.flex-col .name', elem => {
            return elem.innerHTML;
        });
        await expect(appName).toEqual('bing test');

    },30000);

})

describe('一账通-通讯录测试', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let organizationaction = new organizationAction();
        await organizationaction.origanization(page);
        
    },30000)
    afterAll ( async () => {
        await page.close();
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
        
    },100000);

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
        
    },30000);   

})

describe('一账通-个人资料测试', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');
        
    },30000)
    afterAll ( async () => {
        await page.close();
    })


    test('TEST_001:验证个人资料页面链接' , async() => {
        let setaction = new setAction();
        await setaction.setting(page);

        const url = await page.url();
        await expect(url).toMatch('workspace/userinfo');
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

    },30000);

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

    },30000);

    test('TEST_004:验证个人资料页面修改姓名' , async() => {
        let setaction = new setAction();
        await setaction.setting(page);

        const nameInput = await page.waitForSelector('input[placeholder="请输入 姓名"]');
        await nameInput.type("111");

        const saveBtn = await page.waitForSelector('.flex-row.flex-auto .ivu-btn.ivu-btn-primary');
         await saveBtn.click();

         let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

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

    },30000);

})

describe('一账通-账号管理测试', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin'); 

    },60000)
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证账号管理页面链接' , async() => {

        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        await page.waitFor(5000);

        const url = await page.url();
        await expect(url).toMatch('admin/account');
    },30000);

    test('TEST_002:验证账号管理页面添加新账号' , async() => {
        let accountaction = new accountAction();
        await accountaction.addAccount(page, "mxyzz",  "meixinyue", "mei123456", "mei123456", "15822186268", "1821788073@qq.com", "meixinyue11@163.com");         

        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin'); 

        const manageBtn2 = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn2.click();

        await page.waitFor(5000);

        const userName = await page.$eval('.ivu-table-tbody>tr:last-child>td:nth-child(2) span', elem => {
            return elem.innerHTML;
        });
        await expect(userName).toEqual('mxyzz');

        const name = await page.$eval('.ivu-table-tbody>tr:last-child>td:nth-child(3) span', elem => {
            return elem.innerHTML;
        });
        await expect(name).toEqual('meixinyue');

        const phoneNumber = await page.$eval('.ivu-table-tbody>tr:last-child>td:nth-child(4) span', elem => {
            return elem.innerHTML;
        });
        await expect(phoneNumber).toEqual('15822186268');

        const email = await page.$eval('.ivu-table-tbody>tr:last-child>td:nth-child(5) span', elem => {
            return elem.innerHTML;
        });
        await expect(email).toEqual('meixinyue11@163.com');

    },60000);

    test('TEST_003:验证账号管理页面添加新账号后是否生效' , async() => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'mxyzz', 'mei123456'); 

        await page.waitFor(2000);

        const url = await page.url();
        await expect(url).toMatch('#/workspace/apps');
        
    },40000);
})

describe('一账通-账号管理搜索账号', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let accountaction = new accountAction();
        await accountaction.searchAccount(page, "meixinyue");          

    },30000)
    afterAll ( async () => {
        await page.close();
    })

    test('TEST_001:验证账号管理的搜索框' , async() => {
        const name = await page.$eval('.ivu-table-body.ivu-table-overflowX > table > tbody > tr > td:nth-child(2) > div > span:nth-child(1)', elem => {
            return elem.innerHTML;
        });
        await expect(name).toEqual('mxyzz');

    },30000);

})

describe('一账通-账号管理编辑账号', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let accountaction = new accountAction();
        await accountaction.searchAccount(page, "meixinyue");
        await accountaction.reviseAccount(page, "11", "meixinyue", "meixinyue");

    },100000)
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证修改是否生效' , async() => {


        const name = await page.$eval('.ivu-table-row>td:nth-child(3) span', elem => {
            return elem.innerHTML;
        });
        await expect(name).toEqual('meixinyue11');
    },40000);

})


describe('一账通-账号管理编辑账号密码', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'mxyzz', 'meixinyue');

    },40000)
    afterAll ( async () => {
        await page.close();
    })

    test('TEST_001:验证修改密码后能否登录' , async() => {
        await page.waitFor(6000);
        const url = await page.url();
        await expect(url).toMatch('#/workspace/apps');
        
    },40000);

})

describe('一账通-账号管理删除账号', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let accountaction = new accountAction();
        await accountaction.searchAccount(page, "meixinyue");
        await accountaction.deleteAccount(page);

    },50000)
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证删除账号' , async() => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        await page.waitFor(3000);

        const userName = await page.$eval('.ivu-table-tbody>tr:last-child>td:nth-child(2) span', elem => {
            return elem.innerHTML;
        });
        await expect(userName).toEqual('bumen2user');

        
    },50000);

})


describe('一账通-验证分组管理', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

    },60000)
    afterAll ( async () => {
       // await page.close();
    })

    test('TEST_001:验证分组管理页面链接' , async() => {
        let groupaction = new groupAction();
        await groupaction.groupAddress(page);

        const url = await page.url();
        await expect(url).toMatch('#/admin/group/node?id=d_root');
    },30000);

    test('TEST_002:验证分组管理页面添加分组' , async() => {
        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.addGroup(page, "部门四");
        
        const groupName1 = await page.$eval('.ui-group-tree.ivu-tree>ul:last-child .ui-tree-item-title span', elem => {
            return elem.innerHTML;
        });
        await expect(groupName1).toEqual('部门四 ( 0 人 )');

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(1000);

        const groupName2 = await page.$eval('.dept-list>li:last-child .name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(groupName2).toEqual('部门三 (1人)');
    },50000);

})

describe('一账通-验证分组管理分组可见性', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'mei111', 'mei111');

    },30000)
    afterAll ( async () => {
        await page.close();
    })

    test('TEST_001:验证分组管理分组可见性' , async() => {
        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(2000);

        const groupName = await page.$eval('.dept-list>li:last-child .name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(groupName).toEqual('部门三 (1人)');

    },30000);

})

describe('一账通-验证分组管理编辑部门', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');
        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await  groupaction.editGroup(page, "一");

    },30000)
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证修改是否生效' , async() => {

        const groupName1 = await page.$eval('.ui-group-tree.ivu-tree>ul:nth-child(2) .ui-tree-item-title span', elem => {
            return elem.innerHTML;
        });
        await expect(groupName1).toEqual('部门二一 ( 1 人 )');

        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(1000);

        const groupName = await page.$eval('.dept-list>li:nth-child(2) .name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(groupName).toEqual('部门三 (1人)');

    },30000);

})

describe('一账通-验证分组管理编辑部门可见性', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        

    },50000)
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证修改部门可见性是否生效' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'bumen2user', 'bumen2user');

        await page.waitFor(3000);

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(2000);

        const groupName1 = await page.$eval('.dept-list>li:nth-child(2) .name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(groupName1).toEqual('部门二一 (1人)');

    },50000);

})

describe('一账通-验证分组管理添加下级部门', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');
        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.addLowGroup(page, "部门一2");

    },60000)
    afterAll ( async () => {
       // await page.close();
    })

    test('TEST_001:验证分组管理添加下级部门是否生效' , async() => {

        const returnDeskBtn = await page.waitForSelector('div.header-right > a:nth-child(1) > button');
        await returnDeskBtn.click();

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        const groupBtn = await page.waitForSelector('.dept-list>li:first-child');
        await groupBtn.click();

        await page.waitFor(2000);

        const groupName = await page.$eval('.org-main.flex-col .dept-list>li:last-child .name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(groupName).toEqual('部门一2 (0人)');

    },60000);

})

describe('一账通-验证分组管理添加账号', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');
        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.addUser(page, "mei123", "mei123", "mei123", "mei123");

    },30000)
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证分组管理添加账号是否生效' , async() => {

        const userName1 = await page.$eval('div.ivu-table-body.ivu-table-overflowX > table > tbody > tr > td:nth-child(2) > div > span', elem => {
            return elem.innerHTML;
        });
        await expect(userName1).toEqual('mei123');

        const accountBtn = await page.waitForSelector('a[href="#/admin/account"]');
        await accountBtn.click();

        await page.waitFor(2000);

        const userName2 = await page.$eval('.ivu-table-tbody>tr:last-child>td:nth-child(2) span', elem => {
            return elem.innerHTML;
        });
        await expect(userName2).toEqual('mei123');

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(2000);

        const groupBtn = await page.waitForSelector('.dept-list>li:first-child');
        await groupBtn.click();

        const userName3 = await page.$eval('.user-list .name', elem => {
            return elem.innerHTML;
        });
        await expect(userName3).toEqual('mei123');

    },40000);

})

describe('一账通-分组管理编辑账号', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.editUser(page, "3", "mei1233", "mei1233");
       
    },30000)
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证修改是否生效' , async() => {

        const userName1 = await page.$eval('div.ivu-table-body.ivu-table-overflowX > table > tbody > tr > td:nth-child(3) > div > span', elem => {
            return elem.innerHTML;
        });
        await expect(userName1).toEqual('mei1233');

        const accountBtn = await page.waitForSelector('a[href="#/admin/account"]');
        await accountBtn.click();

        await page.waitFor(3000);

        const userName2 = await page.$eval('.ivu-table-tbody>tr:last-child>td:nth-child(3) span', elem => {
            return elem.innerHTML;
        });
        await expect(userName2).toEqual('mei1233');

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(2000);

        const groupBtn = await page.waitForSelector('.dept-list>li:first-child');
        await groupBtn.click();

        const userName3 = await page.$eval('.user-list .name', elem => {
            return elem.innerHTML;
        });
        await expect(userName3).toEqual('mei1233');

    },40000);

})

describe('一账通-分组管理编辑账号密码', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'mei123', 'mei1233');

    },30000)
    afterAll ( async () => {
        await page.close();
    })

    test('TEST_001:验证修改密码后能否登录' , async() => {
        const url = await page.url();
        await expect(url).toMatch('#/workspace/apps');
        
    },30000);

})

describe('一账通-分组管理调整分组', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.editUserGroup(page, "部门三");

    },30000)
    afterAll ( async () => {
        await page.close();
    })

    test('TEST_001:验证调整分组后是否生效' , async() => {
        const groupUserBtn = await page.waitForSelector('.ui-group-tree.ivu-tree>ul:nth-child(3)>li>div');
        await groupUserBtn.click();

        await page.waitFor(2000);

        const userName = await page.$eval('.ivu-table-tbody>tr:last-child>td:nth-child(2) span', elem => {
            return elem.innerHTML;
        });
        await expect(userName).toEqual('mei123');

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(2000);

        const groupBtn = await page.waitForSelector('.dept-list>li:last-child');
        await groupBtn.click();

        await page.waitFor(1000);

        const userName2 = await page.$eval('.user-list>li:last-child .name', elem => {
            return elem.innerHTML;
        });
        await expect(userName2).toEqual('mei1233');


        
    },100000);

})

describe('一账通-分组管理移出分组是否生效', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.removeUserGroup(page);

    },50000)
    afterAll ( async () => {
        await page.close();
    })

    test('TEST_001:验证移出分组后是否生效' , async() => {
        const groupUserBtn = await page.waitForSelector('.ui-group-tree.ivu-tree>ul:nth-child(3)>li>div');
        await groupUserBtn.click();

        await page.waitFor(2000);

        const userName = await page.$eval('div.ivu-table-body.ivu-table-overflowX > table > tbody > tr > td:nth-child(3) > div > span', elem => {
            return elem.innerHTML;
        });
        await expect(userName).toEqual('bumen3user');

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        const groupBtn = await page.waitForSelector('.dept-list>li:last-child');
        await groupBtn.click();

        await page.waitFor(1000);


        const userName2 = await page.$eval('.user-list>li:last-child .name', elem => {
            return elem.innerHTML;
        });
        await expect(userName2).toEqual('bumen3user');
        
    },50000);

})

describe('一账通-分组管理添加自定义分组', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.addPersonalGroup(page, "政治面貌");

    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证添加自定义分组是否生效' , async() => {

        const groupName1 = await page.$eval('.custom-list>li:nth-child(2) span', elem => {
            return elem.innerHTML;
        });
        await expect(groupName1).toEqual('政治面貌');

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        await page.waitFor(2000);

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(2000);
        
        const groupName2 = await page.$eval('.ui-contact-page--side>li:nth-child(7)', elem => {
            return elem.innerHTML;
        });
        await expect(groupName2).toEqual('政治面貌');
        
    },30000);

})

describe('一账通-自定义分类添加分组分组', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.personalUserGroup(page, "团员");

    },30000)
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证自定义分类添加分组后是否生效' , async() => {
        
        const addDirectUserBtn = await page.waitForSelector('.subtitle-wrapper .add');
        await addDirectUserBtn.click();

        await page.waitFor(1000);

        const directUserInput = await page.waitForSelector('div.ivu-drawer-wrap.ui-edit-group > div > div > div > form > div.ivu-form-item.ivu-form-item-required > div > div > input');
        await directUserInput.type("党员");

        const addBtn = await page.waitForSelector('.drawer-footer.flex-row.flex-auto .ivu-btn.ivu-btn-primary');
        await addBtn.click();

        await page.waitFor(2000);

        const perUserGroupName1 = await page.$eval('.ui-group-tree.ivu-tree>ul>li>div>span>span', elem => {
            return elem.innerHTML;
        });
        await expect(perUserGroupName1).toEqual('团员 ( 0 人 )');

        const perUserGroupName2 = await page.$eval('.ui-group-tree.ivu-tree>ul:nth-child(2)>li>div>span>span', elem => {
            return elem.innerHTML;
        });
        await expect(perUserGroupName2).toEqual('党员 ( 0 人 )');

        await page.waitFor(2000);

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        await page.waitFor(2000);

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(2000);

        const groupBtn = await page.waitForSelector('.ui-contact-page--side>li:nth-child(7)');
        await groupBtn.click();

        await page.waitFor(2000);

        const perUserGroupName3 = await page.$eval('.dept-list>li>span', elem => {
            return elem.innerHTML;
        });
        await expect(perUserGroupName3).toEqual('党员 (0人)');


    },50000);

})

describe('一账通-分组管理自定义分类添加分组可见性', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'mei333', 'mei333');

    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证自定义分类添加分组后可见性是否生效' , async() => {
        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        const groupBtn = await page.waitForSelector('.ui-contact-page--side>li:nth-child(7)');
        await groupBtn.click();

        await page.waitFor(2000);

        const perUserGroupName = await page.$eval('.dept-list>li>span', elem => {
            return elem.innerHTML;
        });
        await expect(perUserGroupName).toEqual('党员 (0人)');

    },30000);

})


describe('一账通-分组管理编辑自定义分类下分组', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

    },60000)
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证编辑自定义分类下分组后是否生效' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.editPerGroup(page, "A");

        const perUserGroupName1 = await page.$eval('.ui-group-tree.ivu-tree>ul:last-child .ui-tree-item-title span', elem => {
            return elem.innerHTML;
        });
        await expect(perUserGroupName1).toEqual('团员A ( 0 人 )');

        await page.waitFor(2000);

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        await page.waitFor(2000);

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        const groupBtn = await page.waitForSelector('.ui-contact-page--side>li:nth-child(7)');
        await groupBtn.click();

        await page.waitFor(2000);

        const perUserGroupName2 = await page.$eval('.dept-list>li:last-child .name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(perUserGroupName2).toEqual('团员A (0人)');
        
    },50000);

    test('TEST_001:验证编辑自定义分类下分组可见性后是否生效' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'mei333', 'mei333');

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        const groupBtn = await page.waitForSelector('.ui-contact-page--side>li:nth-child(7)');
        await groupBtn.click();

        await page.waitFor(2000);

        const perUserGroupName2 = await page.$eval('.dept-list>li:last-child .name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(perUserGroupName2).toEqual('团员A (0人)');
        
    },30000);

})

describe('一账通-分组管理自定义分类分组添加下级分组', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.addPerLowGroup(page, "分组一");

    },50000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证自定义分类分组添加下级分组是否生效' , async() => {
        const dirLowGroupName1 = await page.$eval('.ivu-tree-children .ivu-tree-children .ui-tree-item-title span', elem => {
            return elem.innerHTML;
        });
        await expect(dirLowGroupName1).toEqual('分组一 ( 0 人 )');
        
        await page.waitFor(1000);

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(2000);

        const groupBtn = await page.waitForSelector('.ui-contact-page--side>li:nth-child(7)');
        await groupBtn.click();

        const dirUserBtn = await page.waitForSelector('.dept-list>li');
        await dirUserBtn.click();

        const dirLowGroupName2 = await page.$eval('.name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(dirLowGroupName2).toEqual('分组一 (0人)');
        
    },50000);

})


describe('一账通-分组管理自定义分类分组添加成员', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

    },50000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证自定义分类分组添加成员是否生效' , async() => {

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.addPerUser(page, "perectuser", "perectuser", "perectuser", "perectuser");

        const userName1 = await page.$eval('.ivu-table-row>td:nth-child(2) .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(userName1).toEqual('perectuser');

        await page.waitFor(2000);

        const accountBtn = await page.waitForSelector('a[href="#/admin/account"]');
        await accountBtn.click();

        await page.waitFor(3000);

        const userName2 = await page.$eval('.ivu-table-tbody>tr:last-child>td:nth-child(2) span', elem => {
            return elem.innerHTML;
        });
        await expect(userName2).toEqual('perectuser');

        await page.waitFor(2000);

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        await page.waitFor(2000);

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(2000);

        const dirGroupBtn = await page.waitForSelector('.ui-contact-page--side>li:nth-child(7)');
        await dirGroupBtn.click();

        const dirUserBtn = await page.waitForSelector('.dept-list>li');
        await dirUserBtn.click();

        const userName3 = await page.$eval('.user-list .name', elem => {
            return elem.innerHTML;
        });
        await expect(userName3).toEqual('perectuser');
        
    },50000);

    test('TEST_002:验证自定义分类分组添加成员能否登录' , async() => {

        let useraction = new UserAction();
        await useraction.login(page, 'perectuser', 'perectuser');

        const url = await page.url();
        await expect(url).toMatch('#/workspace/apps');
        
    },10000);



})


describe('一账通-分组管理自定义分类分组编辑账号', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.editPerUser(page, "1", "perectuser1", "perectuser1");
       
    },60000)
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证修改是否生效' , async() => {

        const userName1 = await page.$eval('.ivu-table-row>td:nth-child(3) .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(userName1).toEqual('perectuser1');

        await page.waitFor(2000);

        const accountBtn = await page.waitForSelector('a[href="#/admin/account"]');
        await accountBtn.click();

        await page.waitFor(3000);

        const userName2 = await page.$eval('.ivu-table-tbody>tr:last-child>td:nth-child(3) span', elem => {
            return elem.innerHTML;
        });
        await expect(userName2).toEqual('perectuser1');

        await page.waitFor(2000);

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        await page.waitFor(2000);

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(2000);

        const dirGroupBtn = await page.waitForSelector('.ui-contact-page--side>li:nth-child(7)');
        await dirGroupBtn.click();

        const dirUserBtn = await page.waitForSelector('.dept-list>li');
        await dirUserBtn.click();

        const userName3 = await page.$eval('.user-list .name', elem => {
            return elem.innerHTML;
        });
        await expect(userName3).toEqual('perectuser1');

    },50000);

})

describe('一账通-分组管理自定义分类分组编辑账号密码', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'perectuser', 'perectuser1');

    },30000)
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证修改密码后能否登录' , async() => {
        const url = await page.url();
        await expect(url).toMatch('#/workspace/apps');
        
    },30000);

})

describe('一账通-分组管理编辑部门的权限', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');
        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.groupPower(page, "百度");

    },500000)
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证修改权限后是否生效' , async() => {
        
        const powerResult = await page.$eval('.ivu-table-row>td:nth-child(4) .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(powerResult).toEqual('是');
       
        
    },500000);

})

describe('一账通-分组管理编辑部门的权限', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'bumen2user', 'bumen2user');

    },30000)
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证修改权限后是否生效' , async() => {

        const appNameInput = await page.waitForSelector('input[placeholder="搜索应用"]');
        await appNameInput.type("百度");

        await page.waitFor(1000);

        const appName = await page.$eval('.flex-row .name', elem => {
            return elem.innerHTML;
        });
        await expect(appName).toEqual('百度');
       
        
    },30000);

})


describe('一账通-分组管理编辑自定义分组的权限', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');
        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.personalGroupPower(page, "百度");

    },500000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证修改权限后是否生效' , async() => {
        
        const powerResult = await page.$eval('.ivu-table-row>td:nth-child(4) .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(powerResult).toEqual('是');
       
        
    },500000);

})

describe('一账通-分组管理编辑自定义分组的权限', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'axiangmuzuuser', 'axiangmuzuuser');

    },30000)
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证修改权限后是否生效' , async() => {

        const appNameInput = await page.waitForSelector('input[placeholder="搜索应用"]');
        await appNameInput.type("百度");

        await page.waitFor(1000);

        const appName = await page.$eval('.flex-row .name', elem => {
            return elem.innerHTML;
        });
        await expect(appName).toEqual('百度');
       
        
    },30000);

})

describe('一账通-配置管理登录页面', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');
        

    },60000)
    afterAll ( async () => {
        //await page.close();
    })
    
    test('TEST_001:验证配置管理页面链接' , async() => {
        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        await page.waitFor(1000);

        const configManageBtn = await page.waitForSelector('a[href="#/admin/config"]');
        await configManageBtn.click();

        await page.waitFor(2000);

        const url = await page.url();
        await expect(url).toMatch('#/admin/config');
        
    },30000);

    test('TEST_002:验证修改公司面名称是否生效' , async() => {

        let configmanageaction = new configManageAction();
        await configmanageaction.loginSetting(page,"北京龙归科技");
        
        const companyName = await page.$eval('.org-name', elem => {
            return elem.innerHTML;
        });
        await expect(companyName).toEqual('北京龙归科技');
        
    },30000);

    test('TEST_003:验证配置管理页面"去进行账号配置"链接' , async() => {
        let configmanageaction = new configManageAction();
        await configmanageaction.urlTest(page);

        const url = await page.url();
        await expect(url).toMatch('#/admin/account/settings');
        
    },30000);

})

describe('一账通-应用管理添加应用', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

    },60000)
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证添加应用是否生效' , async() => {
        let appsmanageaction = new appsManageAction();
        await appsmanageaction.addApps(page, "携程", "https://www.ctrip.com/", "携程应用");

        const appName = await page.$eval('.ivu-table-tbody>tr:first-child .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(appName).toEqual('携程');

        const mark = await page.$eval('.ivu-table-tbody>tr:first-child>td:nth-child(3) span', elem => {
            return elem.innerHTML;
        });
        await expect(mark).toEqual('携程应用');
    },30000);

    test('TEST_002:验证添加应用在工作台是否生效' , async() => {
        const appName = await page.$eval('.card-list.flex-row>li:first-child .name-intro.flex-col.flex-auto .name', elem => {
            return elem.innerHTML;
        });
        await expect(appName).toEqual('携程');

        const mark = await page.$eval('.card-list.flex-row>li:first-child .name-intro.flex-col.flex-auto .intro', elem => {
            return elem.innerHTML;
        });
        await expect(mark).toEqual('携程应用');
    },30000);

})

describe('一账通-应用管理编辑应用', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');
        
    },30000)
    afterEach ( async () => {
        await page.close();
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
    },30000);

    test('TEST_002:验证编辑应用在工作台是否生效' , async() => {
        const appName = await page.$eval('.card-list.flex-row>li:first-child .name-intro.flex-col.flex-auto .name', elem => {
            return elem.innerHTML;
        });
        await expect(appName).toEqual('携程111');

        const mark = await page.$eval('.card-list.flex-row>li:first-child .name-intro.flex-col.flex-auto .intro', elem => {
            return elem.innerHTML;
        });
        await expect(mark).toEqual('携程应用111');
    },30000);

})

describe('一账通-应用管理删除应用', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');
        
    },30000)
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
    },30000);

    test('TEST_002:验证删除应用在工作台是否生效' , async() => {
        const appName = await page.$eval('.card-list.flex-row>li:first-child .name-intro.flex-col.flex-auto .name', elem => {
            return elem.innerHTML;
        });
        await expect(appName).toEqual('猎聘');

    },30000);

})

describe('一账通-应用管理账号的权限', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');
        let appsmanageaction = new appsManageAction();
        await appsmanageaction.userPower(page, "mei333");
    },350000)
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证账号的权限是否生效' , async() => {
        const resultNameBtn = await page.waitForSelector('.perm-results span');
        await resultNameBtn.click();

        await page.waitFor(2000);

        const resultName = await page.$eval('.ivu-modal-content .ivu-cell-group.name-list .ivu-cell-main .ivu-cell-title', elem => {
            return elem.innerHTML;
        });
        await expect(resultName).toEqual('mei333');
    },350000);

})

describe('一账通-应用管理账号的权限', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'mei333', 'mei333');
    },30000)
    afterAll ( async () => {
        await page.close();
    })

    test('TEST_001:验证账号的权限是否生效' , async() => {
        const appName = await page.$eval('.flex-row .name', elem => {
            return elem.innerHTML;
        });
        await expect(appName).toEqual('猎聘');
    },30000);

})

describe('一账通-应用管理部门的权限', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');
        let appsmanageaction = new appsManageAction();
        await appsmanageaction.departmentPower(page, "部门三");
    },350000)
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证部门的权限是否生效' , async() => {    
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'bumen3user', 'bumen3user');

        const appName = await page.$eval('.flex-row .name', elem => {
            return elem.innerHTML;
        });
        await expect(appName).toEqual('猎聘');
    },30000);

})

describe('一账通-测试设置子管理员', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        await page.waitFor(2000);

        const managerBtn = await page.waitForSelector('a[href="#/admin/manager"]');
        await managerBtn.click();

        await page.waitFor(3000);
        
    },400000)
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证设置子管理员页面链接' , async() => {
        const url = await page.url();
        await expect(url).toMatch('#/admin/manager');
    },30000);

    test('TEST_002:验证设置子管理员是否生效' , async() => {
        let managersettingaction = new managerSettingAction();
        await managersettingaction.managerSetting(page);
        
        const managerName = await page.$eval('.ivu-table-tbody>tr:last-child .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(managerName).toEqual('bumen3user');
    },300000);

})

describe('一账通-测试设置子管理员', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'bumen3user', 'bumen3user');
    },100000)
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证设置子管理员是否生效' , async() => {
        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        const groupBtn = await page.waitForSelector('.header-middle a[href="#/admin/group"]');
        await groupBtn.click();

        await page.waitFor(3000);

        const groupName = await page.$eval('.ui-tree-item.active>span>span', elem => {
            return elem.innerHTML;
        });
        await expect(groupName).toContain('部门三 ( 1 人 )');
    },100000);

})

describe('一账通-测试设置子管理员', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');
        let managersettingaction = new managerSettingAction();
        await managersettingaction.managerSettinga(page, "北京");
    },400000)
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证设置子管理员是否生效' , async() => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        await page.waitFor(2000);

        const managerBtn = await page.waitForSelector('a[href="#/admin/manager"]');
        await managerBtn.click();

        await page.waitFor(3000);

        const managerName = await page.$eval('.ivu-table-tbody>tr:last-child .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(managerName).toEqual('mei111');
    },200000);

})

describe('一账通-测试设置子管理员', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'mei111', 'mei111');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.addUser(page, "mei111add", "mei111add", "mei111add", "mei111add");
    },50000)
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证设置子管理员添加账号是否生效' , async() => {
        
        const userName = await page.$eval('.ivu-table-tbody>tr>td:nth-child(2)>div>span', elem => {
            return elem.innerHTML;
        });
        await expect(userName).toEqual('mei111add');
    },50000);

})

describe('一账通-测试设置子管理员', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');
        let managersettingaction = new managerSettingAction();
        await managersettingaction.managerSettingb(page, "人力");
    },400000)
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证设置子管理员是否生效' , async() => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        await page.waitFor(2000);

        const managerBtn = await page.waitForSelector('a[href="#/admin/manager"]');
        await managerBtn.click();

        await page.waitFor(3000);

        const managerName = await page.$eval('.ivu-table-tbody>tr:last-child .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(managerName).toEqual('mei222');
    },200000);

})

describe('一账通-测试设置子管理员', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false,defaultViewport:{width:1200,height:700}})
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'mei222', 'mei222');
    },400000)
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证设置子管理员添加应用是否生效' , async() => {
        let appsmanageaction = new appsManageAction();
        await appsmanageaction.addApps(page, "测试应用", "", "ceshiyingyong");

        await page.waitFor(3000);

        const appName = await page.$eval('.ivu-table-tbody>tr:last-child>td:nth-child(2) .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(appName).toEqual('测试应用');

        const remarks = await page.$eval('.ivu-table-tbody>tr:last-child>td:nth-child(3) .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(remarks).toEqual('ceshiyingyong');
    },50000);


    test('TEST_001:验证设置子管理员查看日志' , async() => {
        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        await page.waitFor(2000);

        const lookLogBtn = await page.waitForSelector('.header-middle a[href="#/admin/oplog"]');
        await lookLogBtn.click();

        await page.waitFor(3000);

        const loginLog = await page.$eval('.ivu-table-tbody>tr>td>div>div', elem => {
            return elem.innerHTML;
        });
        await expect(loginLog).toEqual('登录');
    },30000);

})

describe('一账通-测试设置子管理员', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');
    },400000)
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证设置子管理员添加应用是否生效' , async() => {
        const appName = await page.$eval('.card-list.flex-row>li:first-child .name', elem => {
            return elem.innerHTML;
        });
        await expect(appName).toEqual('测试应用');

        await page.waitFor(1000);

        const remarks = await page.$eval('.card-list.flex-row>li:first-child .intro', elem => {
            return elem.innerHTML;
        });
        await expect(remarks).toEqual('ceshiyingyong');

    },30000);

})

describe('一账通-测试设置子管理员', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');
        let managersettingaction  = new managerSettingAction();
        await managersettingaction.managerSettingc(page);
    },400000)
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证设置子管理员是否成功' , async() => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        await page.waitFor(2000);

        const managerBtn = await page.waitForSelector('a[href="#/admin/manager"]');
        await managerBtn.click();

        await page.waitFor(3000);

        const managerName = await page.$eval('.ivu-table-tbody>tr:last-child .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(managerName).toEqual('mei333');

    },200000);

})

describe('一账通-测试设置子管理员', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'mei333', 'mei333');
    },400000)
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证设置子管理员公司信息配置' , async() => {
        let configmanageaction = new configManageAction();
        await configmanageaction.loginSetting(page, "111");

        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'mei333', 'mei333');

        const companyName = await page.$eval('.org-name', elem => {
            return elem.innerHTML;
        });
        await expect(companyName).toEqual('北京龙归科技111');
    },400000);

})

describe('一账通-测试设置子管理员', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false,defaultViewport:{width:1200,height:700}})
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');
        let managersettingaction = new managerSettingAction();
        await managersettingaction.managerSettingd(page); 
    },400000)
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证设置子管理员应用权限' , async() => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        await page.waitFor(2000);

        const managerBtn = await page.waitForSelector('a[href="#/admin/manager"]');
        await managerBtn.click();

        await page.waitFor(3000);

        const managerName = await page.$eval('.ivu-table-tbody>tr:last-child .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(managerName).toEqual('axiangmuzuuser');
    },260000);

})

describe('一账通-测试设置子管理员', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'axiangmuzuuser', 'axiangmuzuuser');
    },100000)
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证设置子管理员应用权限' , async() => {
        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        await page.waitFor(2000);

        const appSetBtn = await page.waitForSelector('.header-middle a[href="#/admin/app"]');
        await appSetBtn.click();

        await page.waitFor(3000);

        const appName1 = await page.$eval('.ivu-table-row>td:nth-child(2) span', elem => {
            return elem.innerHTML;
        });
        await expect(appName1).toEqual('测试应用');

        await page.waitFor(2000);

        const editBtn = await page.waitForSelector('.ivu-table-row .flex-row>span:nth-child(2)');
        await editBtn.click();

        await page.waitFor(2000);

        const appNameInput = await page.waitForSelector('input[placeholder="填写应用名称"]');
        await appNameInput.type("111");

        const keepBtn = await page.waitForSelector('.buttons-right .ivu-btn.ivu-btn-primary');
        await keepBtn.click();

        await page.waitFor(3000);

        const appName2 = await page.$eval('.ivu-table-row>td:nth-child(2) span', elem => {
            return elem.innerHTML;
        });
        await expect(appName2).toEqual('测试应用111');

    },100000);

})

describe('一账通-测试编辑子管理员', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let managersettingaction = new managerSettingAction();
        await managersettingaction.editManager(page);

    },400000)
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证编辑子管理员应用权限' , async() => {
        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'axiangmuzuuser', 'axiangmuzuuser');

        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        const logBtn = await page.waitForSelector('.header-middle a[href="#/admin/oplog"]');
        await logBtn.click();

        await page.waitFor(3000);

        const loginLog = await page.$eval('.ivu-table-tbody>tr>td>div>div', elem => {
            return elem.innerHTML;
        });
        await expect(loginLog).toEqual('登录');

    },200000);

})

describe('一账通-测试删除子管理员', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch();
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let managersettingaction = new managerSettingAction();
        await managersettingaction.deleteManager(page);
    },400000)
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证删除子管理员' , async() => {

        let browser = await launch()
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        await page.waitFor(2000);

        const managerBtn = await page.waitForSelector('a[href="#/admin/manager"]');
        await managerBtn.click();

        await page.waitFor(5000);

        const managerName = await page.$eval('.ivu-table-tbody>tr:last-child .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(managerName).toEqual('mei333');

    },80000);

})

describe('一账通-测试操作日志', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch();
        page = await browser.newPage();
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        const logBtn = await page.waitForSelector('.header-middle a[href="#/admin/oplog"]');
        await logBtn.click();

        await page.waitFor(2000);
    },30000)
    afterAll ( async () => {
       // await page.close();
    })

    test('TEST_001:验证操作日志' , async() => {
        
        const loginLog = await page.$eval('.ivu-table-tbody>tr>td>div>div', elem => {
            return elem.innerHTML;
        });
        await expect(loginLog).toEqual('登录');

        const loginLogPer = await page.$eval('.ivu-table-tbody>tr>td:nth-child(2)>div>div', elem => {
            return elem.innerHTML;
        });
        await expect(loginLogPer).toEqual('ad111');

    },30000);

    test('TEST_001:验证查看详细日志' , async() => {

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
        await expect(loginLogPer).toEqual('ad111');

    },30000);

})
