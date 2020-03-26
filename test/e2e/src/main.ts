import {UserAction} from './actions/user'
import {Page, launch} from 'puppeteer';
import {personalSetAction} from './actions/personalSetting';
import {appSearchAction} from './actions/appSearch';
import {organizationAction} from './actions/organization';
import {setAction} from './actions/setting';
import {accountAction} from './actions/account';
import cofig from './config';
import expectPuppeteer = require('expect-puppeteer');
import { appMessageAction } from './actions/appMessage';
import {groupAction} from './actions/group';
import {configManageAction} from './actions/configManage';
import {appsManageAction} from './actions/appsManage';
import {managerSettingAction} from './actions/managerSetting';

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

describe('一账通-退出登录测试', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');
        let personalSetaction = new personalSetAction();
        await personalSetaction.exit(page);

    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证退出链接' , async() => {
        const url = await page.url();
        await expect(url).toContain('https://arkid.demo.longguikeji.com');
    },30000);

})

describe('一账通-修改密码测试', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'mei123', 'mei123');
        let personalSetaction = new personalSetAction();
        await personalSetaction.changePassword(page, "mei123", "meixinyue123", "meixinyue123");

    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证修改密码手否生效' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'mei123', 'meixinyue123');

        const url = await page.url();
        await expect(url).toContain('https://arkid.demo.longguikeji.com/#/workspace/apps');
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
        const appsNum = document.getElementsByTagName(".card-list.flex-row").length;
        //const appsNum = await page.$$('.card-list.flex-row').children('li').length;
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
        await expect(departmentName11).toEqual('部门一1 （0人）');

        const departRetBtn1 = await page.waitForSelector('.path-name');
        await departRetBtn1.click();

        const departmentName2 = await page.$eval('.dept-list>li:nth-child(2) .name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(departmentName2).toEqual('部门二 （1人）');

        const departmentBtn2 = await page.waitForSelector('.dept-list>li:nth-child(2)');
        await departmentBtn2.click();

        const departmentName21 = await page.$eval('.user-list .flex-row .name', elem => {
            return elem.innerHTML;
        });
        await expect(departmentName21).toEqual('部门二成员');

        await departRetBtn1.click();

        const departmentName3 = await page.$eval('.dept-list>li:last-child .name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(departmentName3).toEqual('部门三 （1人）');

        const departmentBtn3 = await page.waitForSelector('.dept-list>li:last-child');
        await departmentBtn3.click();

        
        const departmentName31 = await page.$eval('.user-list .flex-row .name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(departmentName31).toEqual('部门三分组 （0人）');

        const departmentName32 = await page.$eval('.user-list .flex-row .name', elem => {
            return elem.innerHTML;
        });
        await expect(departmentName32).toEqual('部门三成员');

        await departRetBtn1.click();
        
    },30000);

    test('TEST_003:验证通讯录页面的直属成员' , async() => {
        const directBtn = await page.waitForSelector('.ui-contact-page--side>li:nth-child(3)');
        await directBtn.click();

        const membersNum = document.getElementsByTagName(".user-list").length;
        //const membersNum = await page.$$('.user-list').children("li").length;
        await expect(membersNum).toEqual('21');

        const directName1 = await page.$eval('.org-main.flex-col>ul>li:first-child .name', elem => {
            return elem.innerHTML;
        });
        await expect(directName1).toEqual('111111');

        const directName2 = await page.$eval('.org-main.flex-col>ul>li:nth-child(2) .name', elem => {
            return elem.innerHTML;
        });
        await expect(directName2).toEqual('123123');

        const directName3 = await page.$eval('.org-main.flex-col>ul>li:last-child .name', elem => {
            return elem.innerHTML;
        });
        await expect(directName3).toEqual('请尽快修改密码或更改主管理员');

        
    },30000);

    test('TEST_004:验证通讯录页面自定义分类的项目组' , async() => {
        const directBtn = await page.waitForSelector('.ui-contact-page--side>li:nth-child(7)');
        await directBtn.click();

        const departmentName1 = await page.$eval('.dept-list>li:first-child .name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(departmentName1).toEqual('A项目组 (0人)');

        const departmentBtn1 = await page.waitForSelector('.dept-list>li:first-child');
        await departmentBtn1.click();

        const departmentName11 = await page.$eval('.dept-list .name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(departmentName11).toEqual('A项目组1 （0人）');

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
        await expect(departmentName21).toEqual('B项目组成员');

        await departRetBtn1.click();

        const departmentName3 = await page.$eval('.dept-list>li:last-child .name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(departmentName3).toEqual('C项目组 (1人)');

        const departmentBtn3 = await page.waitForSelector('.dept-list>li:last-child');
        await departmentBtn3.click();

        
        const departmentName31 = await page.$eval('.user-list .flex-row .name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(departmentName31).toEqual('C项目组分组 （1人）');

        const departmentName32 = await page.$eval('.user-list .flex-row .name', elem => {
            return elem.innerHTML;
        });
        await expect(departmentName32).toEqual('C项目组成员');

        await departRetBtn1.click();
        
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

describe('一账通-账号管理测试', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');

        let accountaction = new accountAction();
        await accountaction.addAccount(page, "meixinyue", "meixinyue", "mei123456", "mei123456", "15822186268", "1821788073@qq.com", "meixinyue11@163.com", "部门一");          

    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证账号管理页面链接' , async() => {
        const url = await page.url();
        await expect(url).toBe('https://arkid.demo.longguikeji.com/#/admin/account');
    },30000);

    test('TEST_002:验证账号管理页面添加新账号' , async() => {
        const userName = await page.$eval('.ivu-table-tbody>tr:last-child>td:nth-child(2) span', elem => {
            return elem.innerHTML;
        });
        await expect(userName).toEqual('meixinyue');

    },30000);

    test('TEST_003:验证账号管理页面添加新账号后是否生效' , async() => {
        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        const groupBtn = await page.waitForSelector('.dept-list>li:first-child');
        await groupBtn.click();

        const name = await page.$eval('.user-list .flex-row .name', elem => {
            return elem.innerHTML;
        });
        await expect(name).toEqual('meixinyue');

        const usereBtn = await page.waitForSelector('.flex-row.active .name');
        await usereBtn.click();

        const userName = await page.$eval('li[data-label="用户名"]', elem => {
            return elem.innerHTML;
        });
        await expect(userName).toEqual('meixinyue');

        const name2 = await page.$eval('li[data-label="姓名"]', elem => {
            return elem.innerHTML;
        });
        await expect(name2).toEqual('meixinyue');

        const phoneNum = await page.$eval('li[data-label="电话"]', elem => {
            return elem.innerHTML;
        });
        await expect(phoneNum).toEqual('15822186268');

    },30000);
})

describe('一账通-账号管理搜索账号', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');

        let accountaction = new accountAction();
        await accountaction.searchAccount(page, "meixinyue");          

    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证账号管理的搜索框' , async() => {
        const name = await page.$eval('.ivu-table-row>td:nth-child(2) span', elem => {
            return elem.innerHTML;
        });
        await expect(name).toEqual('meixinyue');

    },30000);

})

describe('一账通-账号管理编辑账号', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');

        let accountaction = new accountAction();
        await accountaction.searchAccount(page, "meixinyue");
        await accountaction.reviseAccount(page, "11", "meixinyue", "meixinyue", "部门二");

    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证修改是否生效' , async() => {

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        const groupBtn = await page.waitForSelector('.dept-list>li:first-child');
        await groupBtn.click();

        const name = await page.$eval('.user-list .flex-row .name', elem => {
            return elem.innerHTML;
        });
        await expect(name).toEqual('梅新悦');

        const usereBtn = await page.waitForSelector('.flex-row.active .name');
        await usereBtn.click();

        const name2 = await page.$eval('li[data-label="姓名"]', elem => {
            return elem.innerHTML;
        });
        await expect(name2).toEqual('meixinyue11');

    },30000);

})

describe('一账通-账号管理编辑账号密码', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'meixinyue', 'meixinyue');

    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证修改密码后能否登录' , async() => {
        const url = await page.url();
        await expect(url).toBe('https://arkid.demo.longguikeji.com/#/workspace/apps');
        
    },30000);

})

describe('一账通-账号管理删除账号', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');

        let accountaction = new accountAction();
        await accountaction.searchAccount(page, "meixinyue");
        await accountaction.deleteAccount(page);

    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证删除账号' , async() => {
        await page.waitFor(5000);
        const userName = await page.$eval('.ivu-table-tbody>tr:last-child>td:nth-child(2) span', elem => {
            return elem.innerHTML;
        });
        await expect(userName).toEqual('ffffff');

        
    },30000);

})

describe('一账通-验证分组管理', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.addGroup(page, "部门四");

    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证分组管理页面链接' , async() => {
        const url = await page.url();
        await expect(url).toContain('https://arkid.demo.longguikeji.com/#/admin/group');
    },30000);

    test('TEST_002:验证分组管理页面添加分组' , async() => {
        const groupName1 = await page.$eval('.ui-group-tree.ivu-tree>ul:last-child .ui-tree-item-title span', elem => {
            return elem.innerHTML;
        });
        await expect(groupName1).toEqual('部门四 ( 0 人 )');

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        const groupName2 = await page.$eval('.dept-list>li:last-child .name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(groupName2).toEqual('部门四 ( 0 人 )');
    },30000);

})

describe('一账通-验证分组管理分组可见性', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'mei123', 'mei123');

    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证分组管理分组可见性' , async() => {
        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        const groupName = await page.$eval('.dept-list>li:last-child .name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(groupName).toEqual('部门三 ( 1 人 )');

    },30000);

})

describe('一账通-验证分组管理编辑部门', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');
        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await  groupaction.editGroup(page, "一");

    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证修改是否生效' , async() => {

        const groupName1 = await page.$eval('.ui-group-tree.ivu-tree>ul:last-child .ui-tree-item-title span', elem => {
            return elem.innerHTML;
        });
        await expect(groupName1).toEqual('部门一一 ( 0 人 )');

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        const groupName = await page.$eval('.dept-list>li:first-child .name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(groupName).toEqual('部门一一 ( 0 人 )');

    },30000);

})

describe('一账通-验证分组管理编辑部门可见性', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'mei111', 'mei111');

    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证修改部门可见性是否生效' , async() => {

        const groupName1 = await page.$eval('.dept-list>li:first-child .name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(groupName1).toEqual('部门二 ( 1 人 )');

    },30000);

})

describe('一账通-验证分组管理添加下级部门', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');
        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.addLowGroup(page, "部门一2");

    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证分组管理添加下级部门是否生效' , async() => {

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        const groupBtn = await page.waitForSelector('.dept-list>li:first-child');
        await groupBtn.click();

        const groupName = await page.$eval('.org-main.flex-col .dept-list>li:last-child .name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(groupName).toEqual('部门一2 ( 0 人 )');

    },30000);

})

describe('一账通-验证分组管理添加账号', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');
        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.addUser(page, "mei222", "mei222", "mei222", "mei222");

    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证分组管理添加账号是否生效' , async() => {

        const userName1 = await page.$eval('.ivu-table-row>td:nth-child(2) .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(userName1).toEqual('mei222');

        const accountBtn = await page.waitForSelector('a[href="#/admin/account"]');
        await accountBtn.click();

        const userName2 = await page.$eval('.ivu-table-tbody>tr:last-child>td:nth-child(2) span', elem => {
            return elem.innerHTML;
        });
        await expect(userName2).toEqual('mei222');

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        const groupBtn = await page.waitForSelector('.dept-list>li:first-child');
        await groupBtn.click();

        const userName3 = await page.$eval('.user-list .name', elem => {
            return elem.innerHTML;
        });
        await expect(userName3).toEqual('mei222');

    },30000);

})

describe('一账通-分组管理编辑账号', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.editUser(page, "3", "mei2223", "mei2223");
       
    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证修改是否生效' , async() => {

        const userName1 = await page.$eval('.ivu-table-row>td:nth-child(2) .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(userName1).toEqual('mei2223');

        const accountBtn = await page.waitForSelector('a[href="#/admin/account"]');
        await accountBtn.click();

        const userName2 = await page.$eval('.ivu-table-tbody>tr:last-child>td:nth-child(2) span', elem => {
            return elem.innerHTML;
        });
        await expect(userName2).toEqual('mei2223');

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        const groupBtn = await page.waitForSelector('.dept-list>li:first-child');
        await groupBtn.click();

        const userName3 = await page.$eval('.user-list .name', elem => {
            return elem.innerHTML;
        });
        await expect(userName3).toEqual('mei2223');

    },30000);

})

describe('一账通-分组管理编辑账号密码', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'mei2223', 'mei2223');

    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证修改密码后能否登录' , async() => {
        const url = await page.url();
        await expect(url).toBe('https://arkid.demo.longguikeji.com/#/workspace/apps');
        
    },30000);

})

describe('一账通-分组管理调整分组', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.editUserGroup(page, "部门二");

    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证调整分组后是否生效' , async() => {
        const groupUserBtn = await page.waitForSelector('.ui-group-tree.ivu-tree>ul:nth-child(2) .ui-tree-item-title span');
        await groupUserBtn.click();

        const userName = await page.$eval('.ivu-table-tbody>tr:last-child>td:nth-child(2) span', elem => {
            return elem.innerHTML;
        });
        await expect(userName).toEqual('mei2223');

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        const groupBtn = await page.waitForSelector('.dept-list>li:nth-child(2)');
        await groupBtn.click();

        const userName3 = await page.$eval('.user-list>li:last-child .name', elem => {
            return elem.innerHTML;
        });
        await expect(userName3).toEqual('mei2223');


        
    },30000);

})

describe('一账通-分组管理移出分组是否生效', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.removeUserGroup(page);

    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证移出分组后是否生效' , async() => {
        const userName = await page.$eval('.ivu-table-tbody>tr:last-child>td:nth-child(2) span', elem => {
            return elem.innerHTML;
        });
        await expect(userName).toEqual('mei1122');

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        const groupBtn = await page.waitForSelector('.dept-list>li:nth-child(2)');
        await groupBtn.click();

        const userName3 = await page.$eval('.user-list>li:last-child .name', elem => {
            return elem.innerHTML;
        });
        await expect(userName3).toEqual('mei1122');
        
    },30000);

})

describe('一账通-分组管理删除账号是否生效', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.deleteUserGroup(page);

    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证分组管理删除账号后是否生效' , async() => {
        const userName = await page.$eval('.ivu-table-tbody>tr:last-child>td:nth-child(2) span', elem => {
            return elem.innerHTML;
        });
        await expect(userName).toBeNull();

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        const groupBtn = await page.waitForSelector('.dept-list>li:nth-child(2)');
        await groupBtn.click();

        const userName3 = await page.$eval('.user-list>li:last-child .name', elem => {
            return elem.innerHTML;
        });
        await expect(userName3).toBeNull();
        
    },30000);

})


describe('一账通-分组管理添加直属成员分组', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.directUserGroup(page, "直属成员分组一");

    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证添加直属成员分组后是否生效' , async() => {
        const dirUserGroupName1 = await page.$eval('.ui-tree-item-title span', elem => {
            return elem.innerHTML;
        });
        await expect(dirUserGroupName1).toEqual('直属成员分组一 ( 0 人 )');

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        const groupBtn = await page.waitForSelector('.ui-contact-page--side>li:nth-child(3)');
        await groupBtn.click();

        const dirUserGroupName2 = await page.$eval('.org-main.flex-col .flex-row .name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(dirUserGroupName2).toEqual('直属成员分组一 ( 0 人 )');
        
    },30000);

})

describe('一账通-分组管理添加直属成员分组可见性', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'mei123', 'mei123');

    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证添加直属成员分组后可见性是否生效' , async() => {
        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        const groupBtn = await page.waitForSelector('.ui-contact-page--side>li:nth-child(3)');
        await groupBtn.click();

        const dirUserGroupName2 = await page.$eval('.org-main.flex-col .flex-row .name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(dirUserGroupName2).toBeNull();

    },30000);

})

describe('一账通-分组管理编辑直属成员分组', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.editGroup(page, "1");

    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证编辑直属成员分组后是否生效' , async() => {
        const dirUserGroupName1 = await page.$eval('.ui-tree-item-title span', elem => {
            return elem.innerHTML;
        });
        await expect(dirUserGroupName1).toEqual('直属成员分组一1 ( 0 人 )');

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        const groupBtn = await page.waitForSelector('.ui-contact-page--side>li:nth-child(3)');
        await groupBtn.click();

        const dirUserGroupName2 = await page.$eval('.org-main.flex-col .flex-row .name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(dirUserGroupName2).toEqual('直属成员分组一1 ( 0 人 )');
        
    },30000);

})

describe('一账通-分组管理直属成员分组添加下级分组', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.addDirLowGroup(page, "分组一");

    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证直属成员分组添加下级分组是否生效' , async() => {
        const dirLowGroupName1 = await page.$eval('ul[visible="visible"] .ivu-tree-children .ui-tree-item-title span', elem => {
            return elem.innerHTML;
        });
        await expect(dirLowGroupName1).toEqual('分组一 ( 0 人 )');

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        const groupBtn = await page.waitForSelector('.ui-contact-page--side>li:nth-child(3)');
        await groupBtn.click();

        const dirUserBtn = await page.waitForSelector('.org-main.flex-col .flex-row');
        await dirUserBtn.click();

        const dirLowGroupName2 = await page.$eval('.dept-list .name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(dirLowGroupName2).toEqual('分组一 ( 0 人 )');
        
    },30000);

})

describe('一账通-分组管理直属成员分组添加成员', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.addDirUser(page, "directuser", "directuser", "directuser", "directuser");
    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证直属成员分组添加成员是否生效' , async() => {
        const userName1 = await page.$eval('.ivu-table-row>td:nth-child(2) .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(userName1).toEqual('directuser');

        const accountBtn = await page.waitForSelector('a[href="#/admin/account"]');
        await accountBtn.click();

        const userName2 = await page.$eval('.ivu-table-tbody>tr:last-child>td:nth-child(2) span', elem => {
            return elem.innerHTML;
        });
        await expect(userName2).toEqual('directuser');

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        const dirGroupBtn = await page.waitForSelector('.ui-contact-page--side>li:nth-child(3)');
        await dirGroupBtn.click();

        const groupBtn = await page.waitForSelector('.dept-list>li:first-child');
        await groupBtn.click();

        const userName3 = await page.$eval('.user-list .name', elem => {
            return elem.innerHTML;
        });
        await expect(userName3).toEqual('directuser');
        
    },30000);

})

describe('一账通-分组管理直属成员分组编辑账号', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.editDirUser(page, "1", "directuser1", "directuser1");
       
    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证修改是否生效' , async() => {

        const userName1 = await page.$eval('.ivu-table-row>td:nth-child(2) .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(userName1).toEqual('directuser1');

        const accountBtn = await page.waitForSelector('a[href="#/admin/account"]');
        await accountBtn.click();

        const userName2 = await page.$eval('.ivu-table-tbody>tr:last-child>td:nth-child(2) span', elem => {
            return elem.innerHTML;
        });
        await expect(userName2).toEqual('directuser1');

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        const dirGroupBtn = await page.waitForSelector('.ui-contact-page--side>li:nth-child(3)');
        await dirGroupBtn.click();

        const groupBtn = await page.waitForSelector('.dept-list>li:first-child');
        await groupBtn.click();

        const userName3 = await page.$eval('.user-list .name', elem => {
            return elem.innerHTML;
        });
        await expect(userName3).toEqual('directuser');

    },30000);

})

describe('一账通-分组管理直属分组编辑账号密码', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'directuser', 'directuser1');

    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证修改密码后能否登录' , async() => {
        const url = await page.url();
        await expect(url).toBe('https://arkid.demo.longguikeji.com/#/workspace/apps');
        
    },30000);

})

describe('一账通-分组管理直属分组调整分组', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.editDirUserGroup(page, "部门一");

    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证调整分组后是否生效' , async() => {
        const apartBtn = await page.waitForSelector('.default-list>li');
        await apartBtn.click();

        const userName = await page.$eval('.ivu-table-row>td:nth-child(2) span', elem => {
            return elem.innerHTML;
        });
        await expect(userName).toEqual('directuser1');

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        const groupBtn = await page.waitForSelector('.dept-list>li:nth-child(1)');
        await groupBtn.click();

        const userName3 = await page.$eval('.user-list>li:last-child .name', elem => {
            return elem.innerHTML;
        });
        await expect(userName3).toEqual('directuser1');
        
    },30000);

})

describe('一账通-分组管理添加自定义分组', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.addPersonalGroup(page, "项目组");

    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证添加自定义分组是否生效' , async() => {

        const groupName1 = await page.$eval('.custom-list>li span', elem => {
            return elem.innerHTML;
        });
        await expect(groupName1).toEqual('项目组');

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        const groupName2 = await page.$eval('.ui-contact-page--side>li:nth-child(7)', elem => {
            return elem.innerHTML;
        });
        await expect(groupName2).toEqual('项目组');
        
    },30000);

})

describe('一账通-自定义分类添加分组分组', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.personalUserGroup(page, "A项目组");

    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证自定义分类添加分组后是否生效' , async() => {
        const perUserGroupName1 = await page.$eval('.ui-tree-item-title span', elem => {
            return elem.innerHTML;
        });
        await expect(perUserGroupName1).toEqual('A项目组 ( 0 人 )');

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        const groupBtn = await page.waitForSelector('.ui-contact-page--side>li:nth-child(7)');
        await groupBtn.click();

        const perUserGroupName2 = await page.$eval('.name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(perUserGroupName2).toEqual('A项目组 ( 0 人 )');
        
    },30000);

})

describe('一账通-分组管理自定义分类添加分组可见性', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'mei123', 'mei123');

    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证自定义分类添加分组后可见性是否生效' , async() => {
        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        const groupBtn = await page.waitForSelector('.ui-contact-page--side>li:nth-child(7)');
        await groupBtn.click();

        const perUserGroupName = await page.$eval('.name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(perUserGroupName).toBeNull();

    },30000);

})

describe('一账通-分组管理编辑自定义分类下分组', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.editPerGroup(page, "A");

    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证编辑自定义分类下分组后是否生效' , async() => {
        const perUserGroupName1 = await page.$eval('.ui-tree-item-title span', elem => {
            return elem.innerHTML;
        });
        await expect(perUserGroupName1).toEqual('A项目组A ( 0 人 )');

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        const groupBtn = await page.waitForSelector('.ui-contact-page--side>li:nth-child(7)');
        await groupBtn.click();

        const perUserGroupName2 = await page.$eval('.name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(perUserGroupName2).toEqual('A项目组A ( 0 人 )');
        
    },30000);

})

describe('一账通-分组管理自定义分类分组添加下级分组', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.addPerLowGroup(page, "分组一");

    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证自定义分类分组添加下级分组是否生效' , async() => {
        const dirLowGroupName1 = await page.$eval('.ivu-tree-children .ivu-tree-children .ui-tree-item-title span', elem => {
            return elem.innerHTML;
        });
        await expect(dirLowGroupName1).toEqual('分组一 ( 0 人 )');

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        const groupBtn = await page.waitForSelector('.ui-contact-page--side>li:nth-child(7)');
        await groupBtn.click();

        const dirUserBtn = await page.waitForSelector('.dept-list>li');
        await dirUserBtn.click();

        const dirLowGroupName2 = await page.$eval('.name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(dirLowGroupName2).toEqual('分组一 ( 0 人 )');
        
    },30000);

})

describe('一账通-分组管理自定义分类分组添加成员', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.addPerUser(page, "perectuser", "perectuser", "perectuser", "perectuser");
    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证自定义分类分组添加成员是否生效' , async() => {
        const userName1 = await page.$eval('.ivu-table-row>td:nth-child(2) .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(userName1).toEqual('perectuser');

        const accountBtn = await page.waitForSelector('a[href="#/admin/account"]');
        await accountBtn.click();

        const userName2 = await page.$eval('.ivu-table-tbody>tr:last-child>td:nth-child(2) span', elem => {
            return elem.innerHTML;
        });
        await expect(userName2).toEqual('perectuser');

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        const dirGroupBtn = await page.waitForSelector('.ui-contact-page--side>li:nth-child(7)');
        await dirGroupBtn.click();

        const dirUserBtn = await page.waitForSelector('.dept-list>li');
        await dirUserBtn.click();

        const userName3 = await page.$eval('.user-list .name', elem => {
            return elem.innerHTML;
        });
        await expect(userName3).toEqual('perectuser');
        
    },30000);

})

describe('一账通-分组管理自定义分类分组编辑账号', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.editPerUser(page, "1", "perectuser1", "perectuser1");
       
    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证修改是否生效' , async() => {

        const userName1 = await page.$eval('.ivu-table-row>td:nth-child(2) .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(userName1).toEqual('perectuser1');

        const accountBtn = await page.waitForSelector('a[href="#/admin/account"]');
        await accountBtn.click();

        const userName2 = await page.$eval('.ivu-table-tbody>tr:last-child>td:nth-child(2) span', elem => {
            return elem.innerHTML;
        });
        await expect(userName2).toEqual('perectuser1');

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        const dirGroupBtn = await page.waitForSelector('.ui-contact-page--side>li:nth-child(7)');
        await dirGroupBtn.click();

        const groupBtn = await page.waitForSelector('.dept-list>li');
        await groupBtn.click();

        const userName3 = await page.$eval('.user-list .name', elem => {
            return elem.innerHTML;
        });
        await expect(userName3).toEqual('perectuser1');

    },30000);

})

describe('一账通-分组管理自定义分类分组编辑账号密码', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'perectuser', 'perectuser1');

    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证修改密码后能否登录' , async() => {
        const url = await page.url();
        await expect(url).toBe('https://arkid.demo.longguikeji.com/#/workspace/apps');
        
    },30000);

})

describe('一账通-分组管理编辑部门的权限', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');
        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.groupPower(page, "街道OA");

    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证修改权限后是否生效' , async() => {
        
        const powerResult = await page.$eval('.ivu-table-row>td:nth-child(4) .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(powerResult).toEqual('是');
       
        
    },30000);

})

describe('一账通-分组管理编辑部门的权限', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'mei123', 'mei123');

    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证修改权限后是否生效' , async() => {

        const appNameInput = await page.waitForSelector('input[placeholder="搜索应用"]');
        await appNameInput.type("街道OA");

        const appName = await page.$eval('.flex-row .name', elem => {
            return elem.innerHTML;
        });
        await expect(appName).toEqual('街道OA');
       
        
    },30000);

})

describe('一账通-分组管理编辑自定义分组的权限', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');
        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.personalGroupPower(page, "街道OA");

    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证修改权限后是否生效' , async() => {
        
        const powerResult = await page.$eval('.ivu-table-row>td:nth-child(4) .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(powerResult).toEqual('是');
       
        
    },30000);

})

describe('一账通-分组管理编辑自定义分组的权限', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'xiangmuzua', 'xiangmuzua');

    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证修改权限后是否生效' , async() => {

        const appNameInput = await page.waitForSelector('input[placeholder="搜索应用"]');
        await appNameInput.type("街道OA");

        const appName = await page.$eval('.flex-row .name', elem => {
            return elem.innerHTML;
        });
        await expect(appName).toEqual('街道OA');
       
        
    },30000);

})

describe('一账通-配置管理登录页面', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');
        let configmanageaction = new configManageAction();
        await configmanageaction.loginSetting(page,"北京龙归科技");
        let personalsettingaction = new personalSetAction();
        await personalsettingaction.exit(page);

    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证修改公司面名称是否生效' , async() => {
        const companyName = await page.$eval('.org-name', elem => {
            return elem.innerHTML;
        });
        await expect(companyName).toEqual('北京龙归科技');
        
    },30000);

    test('TEST_002:验证配置管理页面链接' , async() => {
        let configmanageaction = new configManageAction();
        await configmanageaction.urlTest(page);

        const url = await page.url();
        await expect(url).toBe('https://arkid.demo.longguikeji.com/#/admin/account');
        
    },30000);


})

describe('一账通-应用管理添加应用', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');
        let appsmanageaction = new appsManageAction();
        await appsmanageaction.addApps(page, "bing test", "https://cn.bing.com/", "微软Bing搜索");

    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证添加应用是否生效' , async() => {
        const appName = await page.$eval('.ivu-table-tbody>tr:last-child .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(appName).toEqual('bing test');

        const mark = await page.$eval('.ivu-table-tbody>tr:last-child>td:nth-child(3) span', elem => {
            return elem.innerHTML;
        });
        await expect(mark).toEqual('微软Bing搜索');
    },30000);

})

describe('一账通-应用管理添加应用在我的应用是否生效', () => {
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

    test('TEST_001:验证添加应用是否生效' , async() => {
        const appName = await page.$eval('.card-list.flex-row>li:last-child .name-intro.flex-col.flex-auto .name', elem => {
            return elem.innerHTML;
        });
        await expect(appName).toEqual('bing test');

        const mark = await page.$eval('.card-list.flex-row>li:last-child .name-intro.flex-col.flex-auto .intro', elem => {
            return elem.innerHTML;
        });
        await expect(mark).toEqual('微软Bing搜索');
    },30000);

    test('TEST_002:验证添加应用的链接是否正确' , async() => {
        const appUrlBtn = await page.waitForSelector('.card-list.flex-row>li:last-child');
        await appUrlBtn.click();

        const appUrl = await page.url();
        await expect(appUrl).toBe('https://cn.bing.com/');
    },30000);
})


describe('一账通-应用管理编辑应用', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');
        let appsmanageaction = new appsManageAction();
        await appsmanageaction.editAppMassage(page, "bing test111",  "微软Bing搜索111");

    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证添加应用是否生效' , async() => {
        const appName = await page.$eval('.ivu-table-tbody>tr:last-child .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(appName).toEqual('bing test111');

        const mark = await page.$eval('.ivu-table-tbody>tr:last-child>td:nth-child(3) span', elem => {
            return elem.innerHTML;
        });
        await expect(mark).toEqual('微软Bing搜索111');
    },30000);

})

describe('一账通-应用管理添加应用在我的应用是否生效', () => {
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

    test('TEST_001:验证添加应用是否生效' , async() => {
        const appName = await page.$eval('.card-list.flex-row>li:last-child .name-intro.flex-col.flex-auto .name', elem => {
            return elem.innerHTML;
        });
        await expect(appName).toEqual('bing test111');

        const mark = await page.$eval('.card-list.flex-row>li:last-child .name-intro.flex-col.flex-auto .intro', elem => {
            return elem.innerHTML;
        });
        await expect(mark).toEqual('微软Bing搜索111');
    },30000);

})

describe('一账通-应用管理编辑应用', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');
        let appsmanageaction = new appsManageAction();
        await appsmanageaction.editAppMassage(page, "bing test111",  "微软Bing搜索111");

    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证删除应用是否生效' , async() => {
        const appName = await page.$eval('.ivu-table-tbody>tr:last-child .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(appName).toEqual('街道OA');

        const mark = await page.$eval('.ivu-table-tbody>tr:last-child>td:nth-child(3) span', elem => {
            return elem.innerHTML;
        });
        await expect(mark).toBeNull();
    },30000);

})

describe('一账通-应用管理删除应用', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');
        let appsmanageaction = new appsManageAction();
        await appsmanageaction.deleteApp(page);
    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证删除应用是否生效' , async() => {
        const appName = await page.$eval('.card-list.flex-row>li:last-child .name-intro.flex-col.flex-auto .name', elem => {
            return elem.innerHTML;
        });
        await expect(appName).toEqual('街道OA');

        const mark = await page.$eval('.card-list.flex-row>li:last-child .name-intro.flex-col.flex-auto .intro', elem => {
            return elem.innerHTML;
        });
        await expect(mark).toBeNull();
    },30000);

})

describe('一账通-应用管理账号的权限', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');
        let appsmanageaction = new appsManageAction();
        await appsmanageaction.userPower(page, "mei123");
    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证账号的权限是否生效' , async() => {
        const resultNameBtn = await page.waitForSelector('.perm-results span');
        await resultNameBtn.click();

        const resultName = await page.$eval('.ivu-modal-content .ivu-cell-group.name-list .ivu-cell-main .ivu-cell-title', elem => {
            return elem.innerHTML;
        });
        await expect(resultName).toEqual('mei123');
    },30000);

})

describe('一账通-应用管理账号的权限', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'mei123', 'mei123');
    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证账号的权限是否生效' , async() => {
        const appName = await page.$eval('.flex-row .name', elem => {
            return elem.innerHTML;
        });
        await expect(appName).toEqual('百度');
    },30000);

})

describe('一账通-应用管理部门的权限', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');
        let appsmanageaction = new appsManageAction();
        await appsmanageaction.departmentPower(page, "部门一");
    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证部门的权限是否生效' , async() => {
        const resultNameBtn = await page.waitForSelector('.perm-results span');
        await resultNameBtn.click();

        const resultName = await page.$eval('.ivu-modal-content .ivu-cell-group.name-list .ivu-cell-main .ivu-cell-title', elem => {
            return elem.innerHTML;
        });
        await expect(resultName).toEqual('部门一');
    },30000);

})

describe('一账通-应用管理部门的权限', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'mei123456', 'mei123456');
    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证账号的权限是否生效' , async() => {
        const appName = await page.$eval('.flex-row .name', elem => {
            return elem.innerHTML;
        });
        await expect(appName).toEqual('百度');
    },30000);

})

describe('一账通-应用管理自定义分组的权限', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');
        let appsmanageaction = new appsManageAction();
        await appsmanageaction.personalGroupPower(page, "项目组A");
    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证自定义分组的权限是否生效' , async() => {
        const resultNameBtn = await page.waitForSelector('.perm-results span');
        await resultNameBtn.click();

        const resultName = await page.$eval('.ivu-modal-content .ivu-cell-group.name-list .ivu-cell-main .ivu-cell-title', elem => {
            return elem.innerHTML;
        });
        await expect(resultName).toEqual('项目组A');
    },30000);

})

describe('一账通-测试设置子管理员', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'longguikeji');
        let managersettingaction = new managerSettingAction();
        await managersettingaction.managerSetting(page, "部门");
    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证设置子管理员是否生效' , async() => {
        const managerName = await page.$eval('.ivu-table-tbody>tr:last-child .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(managerName).toEqual('mei123');
    },30000);

})

describe('一账通-测试设置子管理员', () => {
    let page : Page;
    
    beforeEach( async () => {
        let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
        page = await browser.newPage();
        await page.goto(cofig.url);

        let useraction = new UserAction();
        await useraction.login(page, 'mei123', 'mei123');
    },30000)
    afterEach ( async () => {
        await page.close();
    })

    test('TEST_001:验证设置子管理员是否生效' , async() => {
        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        const groupBtn = await page.waitForSelector('.header-middle a[href="#/admin/group"]');
        await groupBtn.click();

        const groupName = await page.$eval('.ui-tree-item.active .ui-tree-item-title span', elem => {
            return elem.innerHTML;
        });
        await expect(groupName).toEqual('部门 一1 ( 2 人 )');
    },30000);

})