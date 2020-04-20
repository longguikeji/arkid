import { UserAction } from './actions/user';
import {Page, launch} from 'puppeteer';
import {appSearchAction} from './actions/appSearch';
import config from './config';
import expectPuppeteer = require('expect-puppeteer');
import {groupAction} from './actions/group';
import {accountAction} from './actions/account';

declare var global: any

describe('一账通-验证分组管理', () => {
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

    },180000)
    afterAll ( async () => {
       // await page.close();
    })

    test('TEST_001:验证分组管理页面链接' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);

        const url = await page.url();
        await expect(url).toMatch('#/admin/group');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    },80000);

    test('TEST_002:验证分组管理页面添加分组' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

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

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    },50000);

    test('TEST_003:验证分组管理分组可见性' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'mei111', 'mei111');

        await page.waitFor(2000);

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(2000);

        const groupName = await page.$eval('.dept-list>li:last-child .name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(groupName).toEqual('部门三 (1人)');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    },50000);

})

describe('一账通-验证分组管理添加下级部门', () => {
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
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

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    },60000);

})

describe('一账通-验证分组管理添加账号', () => {
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');
        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.addUser(page, "mei123", "mei123", "mei123", "mei123");

    },100000)
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

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    },60000);

})

describe('一账通-分组管理编辑账号', () => {
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);
       
    },80000)
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证修改是否生效' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.editUser(page, "3", "meixinyue", "meixinyue");

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

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    },40000);

    test('TEST_001:验证修改密码后能否登录' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'mei123', 'meixinyue');

        const url = await page.url();
        await expect(url).toMatch('#/workspace/apps');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
        
    },30000);

})

describe('一账通-分组管理调整分组', () => {
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

    },100000)
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证调整分组后是否生效' , async() => {
        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.editUserGroup(page, "部门三");

        const groupUserBtn = await page.waitForSelector('.ui-group-tree.ivu-tree>ul:nth-child(3)>li>div');
        await groupUserBtn.click();

        await page.waitFor(2000);

        const userName = await page.$eval('.ivu-table-tbody>tr:last-child>td:nth-child(2) span', elem => {
            return elem.innerHTML;
        });
        await expect(userName).toEqual('bumen2user');

        await page.waitFor(2000);

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
        await expect(userName2).toEqual('bumen2user');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    },50000);

})

describe('一账通-分组管理移出分组', () => {
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

    },50000)
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_002:验证移出分组后是否生效' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.removeUserGroup(page);

        const groupUserBtn = await page.waitForSelector('.ui-group-tree.ivu-tree>ul:nth-child(3)>li>div');
        await groupUserBtn.click();

        await page.waitFor(2000);

        const userName = await page.$eval('div.ivu-table-body.ivu-table-overflowX > table > tbody > tr > td:nth-child(3) > div > span', elem => {
            return elem.innerHTML;
        });
        await expect(userName).toEqual('bumen3user');

        await page.waitFor(2000);

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        await page.waitFor(2000);

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        const groupBtn = await page.waitForSelector('.dept-list>li:last-child');
        await groupBtn.click();

        await page.waitFor(1000);

        const userName2 = await page.$eval('.user-list>li:last-child .name', elem => {
            return elem.innerHTML;
        });
        await expect(userName2).toEqual('bumen3user');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
        
    },50000);

})

describe('一账通-分组管理添加自定义分组', () => {
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

    },200000)
    afterEach ( async () => {
        //await page.close();
    })

    test('TEST_001:验证添加自定义分类是否生效' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.addPersonalGroup(page, "政治面貌");

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

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
        
    },30000);

})

describe('一账通-自定义分类添加分组分组', () => {
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
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

        const perUserGroupName1 = await page.$eval('.ui-group-tree.ivu-tree>ul>li>div>span>span', elem => {
            return elem.innerHTML;
        });
        await expect(perUserGroupName1).toEqual('团员 ( 0 人 )');

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        await page.waitFor(2000);

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(2000);

        const groupBtn = await page.waitForSelector('.ui-contact-page--side>li:nth-child(7)');
        await groupBtn.click();

        await page.waitFor(2000);

        const perUserGroupName3 = await page.$eval('.dept-list>li:last-child .name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(perUserGroupName3).toEqual('团员 (0人)');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    },50000);

})

describe('一账通-分组管理编辑自定义分类下分组', () => {
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

    },150000)
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
        await expect(perUserGroupName1).toEqual('A项目组A ( 1 人 )');

        await page.waitFor(2000);

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        await page.waitFor(2000);

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        const groupBtn = await page.waitForSelector('.ui-contact-page--side>li:nth-child(6)');
        await groupBtn.click();

        await page.waitFor(2000);

        const perUserGroupName2 = await page.$eval('.dept-list>li:last-child .name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(perUserGroupName2).toEqual('A项目组A (0人)');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
        
    },50000);

    test('TEST_001:验证编辑自定义分类下分组可见性后是否生效' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'mei333', 'mei333');
        
        await page.waitFor(2000);

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        const groupBtn = await page.waitForSelector('.ui-contact-page--side>li:nth-child(6)');
        await groupBtn.click();

        await page.waitFor(2000);

        const perUserGroupName2 = await page.$eval('.dept-list>li:last-child .name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(perUserGroupName2).toEqual('A项目组A (0人)');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
        
    },50000);

})

describe('一账通-分组管理自定义分类分组添加下级分组', () => {
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.addPerLowGroup(page, "分组一");

    },50000)
    afterEach ( async () => {
       // await page.close();
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

        const groupBtn = await page.waitForSelector('.ui-contact-page--side>li:nth-child(6)');
        await groupBtn.click();

        const dirUserBtn = await page.waitForSelector('.dept-list>li');
        await dirUserBtn.click();

        const dirLowGroupName2 = await page.$eval('.dept-list>li:last-child .name.flex-auto', elem => {
            return elem.innerHTML;
        });
        await expect(dirLowGroupName2).toEqual('分组一 (0人)');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
        
    },50000);

})

describe('一账通-分组管理自定义分类分组添加成员', () => {
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

    },80000)
    afterEach ( async () => {
       // await page.close();
    })

    test('TEST_001:验证自定义分类分组添加成员是否生效' , async() => {

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.addPerUser(page, "perectuser", "perectuser", "perectuser", "perectuser");

        const userName1 = await page.$eval('.ivu-table-tbody>tr:last-child>td:nth-child(2) .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(userName1).toEqual('perectuser');

        await page.waitFor(2000);

        // const accountBtn = await page.waitForSelector('a[href="#/admin/account"]');
        // await accountBtn.click();

        // await page.waitFor(3000);

        // const userName2 = await page.$eval('.ivu-table-tbody>tr:last-child>td:nth-child(2) span', elem => {
        //     return elem.innerHTML;
        // });
        // await expect(userName2).toEqual('perectuser');

        // await page.waitFor(2000);

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        await page.waitFor(2000);

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(2000);

        const dirGroupBtn = await page.waitForSelector('.ui-contact-page--side>li:nth-child(6)');
        await dirGroupBtn.click();

        const dirUserBtn = await page.waitForSelector('.dept-list>li');
        await dirUserBtn.click();

        const userName3 = await page.$eval('.user-list>li:last-child .name', elem => {
            return elem.innerHTML;
        });
        await expect(userName3).toEqual('perectuser');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
        
    },50000);

    test('TEST_002:验证自定义分类分组添加成员能否登录' , async() => {

        let useraction = new UserAction();
        await useraction.login(page, 'perectuser', 'perectuser');

        const url = await page.url();
        await expect(url).toMatch('#/workspace/apps');
        
        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    },30000);

})

describe('一账通-分组管理自定义分类分组编辑账号', () => {
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);
       
    },80000)
    afterAll ( async () => {

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    })

    test('TEST_001:验证修改是否生效' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.editPerUser(page, "1", "aaaaaa", "aaaaaa");

        const userName1 = await page.$eval('.ivu-table-row>td:nth-child(3) .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(userName1).toEqual('bxiangmuzuuser1');

        await page.waitFor(2000);

        // const accountBtn = await page.waitForSelector('a[href="#/admin/account"]');
        // await accountBtn.click();

        // await page.waitFor(3000);
        
        // let accountaction = new accountAction();
        // await accountaction.searchAccount(page, "bxiangmuzuuser");
        // await page.waitFor(4000);

        // const userName2 = await page.$eval('.ivu-table-tbody>tr:last-child>td:nth-child(3) span', elem => {
        //     return elem.innerHTML;
        // });
        // await expect(userName2).toEqual('bxiangmuzuuser1');

        // await page.waitFor(2000);

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        await page.waitFor(2000);

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(2000);

        const dirGroupBtn = await page.waitForSelector('.ui-contact-page--side>li:nth-child(6)');
        await dirGroupBtn.click();

        const dirUserBtn = await page.waitForSelector('.dept-list>li');
        await dirUserBtn.click();

        const userName3 = await page.$eval('.user-list .name', elem => {
            return elem.innerHTML;
        });
        await expect(userName3).toEqual('bxiangmuzuuser1');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();        

    },50000);

    test('TEST_002:验证修改密码后能否登录' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'bxiangmuzuuser', 'aaaaaa');

        const url = await page.url();
        await expect(url).toMatch('#/workspace/apps');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
        
    },30000);

})
/*
describe('一账通-分组管理编辑部门的权限', () => {
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

    },530000)
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证修改权限后是否生效' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');
        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.groupPower(page, "百度");
        
        const powerResult = await page.$eval('.ivu-table-row>td:nth-child(4) .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(powerResult).toEqual('是');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
       
    },500000);

})

describe('一账通-分组管理编辑部门的权限', () => {
    let page : Page;

    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

    },530000)
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_002:验证修改权限后是否生效' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'bumen2user', 'bumen2user');

        const appNameInput = await page.waitForSelector('input[placeholder="搜索应用"]');
        await appNameInput.type("百度");

        await page.waitFor(1000);

        const appName = await page.$eval('.flex-row .name', elem => {
            return elem.innerHTML;
        });
        await expect(appName).toEqual('百度');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
        
    },30000);

})

describe('一账通-分组管理编辑自定义分组的权限', () => {
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');
        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.personalGroupPower(page, "百度");

    },530000)
    afterEach ( async () => {
        //await page.close();
    })

    test('TEST_001:验证修改权限后是否生效' , async() => {
        
        const powerResult = await page.$eval('.ivu-table-row>td:nth-child(4) .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(powerResult).toEqual('是');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
       
    },500000);

})

describe('一账通-分组管理自定义分组的权限', () => {
    let page : Page;

    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

    },530000)
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证修改权限后是否生效' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'bxiangmuzuuser', 'aaaaaa');

        const appNameInput = await page.waitForSelector('input[placeholder="搜索应用"]');
        await appNameInput.type("百度");

        await page.waitFor(1000);

        const appName = await page.$eval('.flex-row .name', elem => {
            return elem.innerHTML;
        });
        await expect(appName).toEqual('百度');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
        
    },30000);

})
*/
