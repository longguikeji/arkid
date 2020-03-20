import {UserAction} from './actions/user'
import {Page, launch} from 'puppeteer';
import {appSearchAction} from './actions/appSearch';
import {organizationAction} from './actions/organization';
import {setAction} from './actions/setting';
import {accountAction} from './actions/account';
import cofig from './config';
import expectPuppeteer = require('expect-puppeteer');
import { appMessageAction } from './actions/appMessage';
import {groupAction} from './actions/group';



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
        await accountaction.reviseAccount(page, "梅新悦", "meixinyue", "meixinyue", "13782921749", "meixinyue11@163.com", "1821788073@qq.com","部门二");

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
        await expect(name2).toEqual('梅新悦');

        const phoneNum = await page.$eval('li[data-label="电话"]', elem => {
            return elem.innerHTML;
        });
        await expect(phoneNum).toEqual('13782921749');
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