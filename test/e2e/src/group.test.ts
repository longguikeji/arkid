import { UserAction } from './actions/user';
import {Page, launch} from 'puppeteer';
import {appSearchAction} from './actions/appSearch';
import config from './config';
import expectPuppeteer = require('expect-puppeteer');
import {groupAction} from './actions/group';
import {accountAction} from './actions/account';

declare var global: any
jest.setTimeout(600000);

describe('一账通-验证分组管理', () => {
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

    })
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

    });

    test('TEST_002:验证分组管理页面添加分组' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.addGroup(page, "部门四");
       
        await page.waitFor(5000);

        const groupName1 = await page.$eval('div.ui-group-tree-component.tree > div.ui-group-tree-wrapper > div > ul:nth-child(4) > li > div > span > span', elem => {
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

    });

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

    });

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

    })
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

    });

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

    })
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

    });

})

describe('一账通-分组管理编辑账号', () => {
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);
       
    })
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证修改是否生效' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.editUser(page, "3", "meixinyue", "meixinyue");

        await page.waitFor(3000);

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

    });

    test('TEST_001:验证修改密码后能否登录' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'mei123', 'meixinyue');

        const url = await page.url();
        await expect(url).toMatch('#/workspace/apps');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
        
    });

})

describe('一账通-分组管理调整分组', () => {
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

    });

})

describe('一账通-分组管理移出分组', () => {
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

    })
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
        
    });

})

describe('一账通-分组管理添加自定义分组', () => {
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

    })
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
        
    });

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

    })
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

    });

})

describe('一账通-分组管理编辑自定义分类下分组', () => {
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

    })
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
        
    });

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
        
    });

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

    })
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
        
    });

})

describe('一账通-分组管理自定义分类分组添加成员', () => {
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

    })
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
        
    });

    test('TEST_002:验证自定义分类分组添加成员能否登录' , async() => {

        let useraction = new UserAction();
        await useraction.login(page, 'perectuser', 'perectuser');

        const url = await page.url();
        await expect(url).toMatch('#/workspace/apps');
        
        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    });

})

describe('一账通-分组管理自定义分类分组编辑账号', () => {
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);
       
    })
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

    });

    test('TEST_002:验证修改密码后能否登录' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'bxiangmuzuuser', 'aaaaaa');

        const url = await page.url();
        await expect(url).toMatch('#/workspace/apps');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
        
    });

})

describe('一账通-验证分组可见性-仅组内成员可见（下属分组不可见）', () => {
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);
       
    })
    afterAll ( async () => {

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    })

    test('TEST_001:仅组内成员可见（下属分组不可见）' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);

        const groupBtn = await page.waitForSelector('.ui-group-tree.ivu-tree>ul:nth-child(3)>li .ivu-tree-children');
        await groupBtn.click();
          
        await page.waitFor(2000);

        await groupaction.addUser(page, "mei6666", "mei6666", "mei6666", "mei6666");

        await page.waitFor(2000);

        const groupBtn2 = await page.waitForSelector('.ui-group-tree.ivu-tree>ul:nth-child(3) .ui-tree-item-bg');
        await groupBtn2.click();

        const editGroupBtn = await page.waitForSelector('.ui-group-page-detail-header.flex-row>button');
        await editGroupBtn.click();

        await page.waitFor(2000);

        const visibleBtn = await page.waitForSelector('div.ivu-drawer-wrap.ui-edit-group > div > div > div > form > div:nth-child(3) > div > div > div.ivu-select-selection');
        await visibleBtn.click();

        const visibleTwo = await page.waitForSelector('div.ivu-drawer-wrap.ui-edit-group > div > div > div > form > div:nth-child(3) > div > div > div.ivu-select-dropdown > ul.ivu-select-dropdown-list > li:nth-child(2)');
        await visibleTwo.click();

        const keepBtn = await page.waitForSelector('.drawer-footer.flex-row.flex-auto>button:last-child');
        await keepBtn.click();

        await page.waitFor(2000);

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        await page.waitFor(2000);

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(2000);

        const departName = await page.$eval('.dept-list>li:last-child span', elem => {
            return elem.innerHTML;
        });
        await expect(departName).toEqual('部门三 (1人)');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();        

    });

    test('TEST_002:仅组内成员可见（下属分组不可见）组内成员登录' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'bumen3user', 'bumen3user');

        await page.waitFor(2000);

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(2000);

        const departName = await page.$eval('.dept-list>li:last-child span', elem => {
            return elem.innerHTML;
        });
        await expect(departName).toEqual('部门三 (2人)');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
        
    });

    test('TEST_003:仅组内成员可见（下属分组不可见）下属分组成员登录' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'mei6666', 'mei6666');

        await page.waitFor(2000);

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(2000);

        const departName = await page.$eval('.dept-list>li:last-child span', elem => {
            return elem.innerHTML;
        });
        await expect(departName).toEqual('部门三 (1人)');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
        
    });

})

describe('一账通-验证分组可见性-组内成员及其下属分组可见', () => {
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);
       
    })
    afterAll ( async () => {

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    })

    test('TEST_001:组内成员及其下属分组可见' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);

        const groupBtn2 = await page.waitForSelector('.ui-group-tree.ivu-tree>ul:nth-child(3) .ui-tree-item-bg');
        await groupBtn2.click();

        const editGroupBtn = await page.waitForSelector('.ui-group-page-detail-header.flex-row>button');
        await editGroupBtn.click();

        await page.waitFor(2000);

        const visibleBtn = await page.waitForSelector('div.ivu-drawer-wrap.ui-edit-group > div > div > div > form > div:nth-child(3) > div > div > div.ivu-select-selection');
        await visibleBtn.click();

        const visibleThree = await page.waitForSelector('div.ivu-drawer-wrap.ui-edit-group > div > div > div > form > div:nth-child(3) > div > div > div.ivu-select-dropdown > ul.ivu-select-dropdown-list > li:nth-child(3)');
        await visibleThree.click();

        const keepBtn = await page.waitForSelector('.drawer-footer.flex-row.flex-auto>button:last-child');
        await keepBtn.click();

        await page.waitFor(2000);

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        await page.waitFor(2000);

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(2000);

        const departName = await page.$eval('.dept-list>li:last-child span', elem => {
            return elem.innerHTML;
        });
        await expect(departName).toEqual('部门三 (1人)');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();        

    });

    test('TEST_002:组内成员及其下属分组可见 组内成员登录' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'bumen3user', 'bumen3user');

        await page.waitFor(2000);

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(2000);

        const departName = await page.$eval('.dept-list>li:last-child span', elem => {
            return elem.innerHTML;
        });
        await expect(departName).toEqual('部门三 (2人)');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
        
    });

    test('TEST_003:组内成员及其下属分组可见 下属分组成员登录' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'mei6666', 'mei6666');

        await page.waitFor(2000);

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(2000);

        const departName = await page.$eval('.dept-list>li:last-child span', elem => {
            return elem.innerHTML;
        });
        await expect(departName).toEqual('部门三 (2人)');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
        
    });

})

describe('一账通-验证分组可见性-所有人不可见', () => {
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);
       
    })
    afterAll ( async () => {

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    })

    test('TEST_001:所有人不可见' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);

        const groupBtn2 = await page.waitForSelector('.ui-group-tree.ivu-tree>ul:nth-child(3) .ui-tree-item-bg');
        await groupBtn2.click();

        const editGroupBtn = await page.waitForSelector('.ui-group-page-detail-header.flex-row>button');
        await editGroupBtn.click();

        await page.waitFor(2000);

        const visibleBtn = await page.waitForSelector('div.ivu-drawer-wrap.ui-edit-group > div > div > div > form > div:nth-child(3) > div > div > div.ivu-select-selection');
        await visibleBtn.click();

        const visibleFour = await page.waitForSelector('div.ivu-drawer-wrap.ui-edit-group > div > div > div > form > div:nth-child(3) > div > div > div.ivu-select-dropdown > ul.ivu-select-dropdown-list > li:nth-child(4)');
        await visibleFour.click();

        const keepBtn = await page.waitForSelector('.drawer-footer.flex-row.flex-auto>button:last-child');
        await keepBtn.click();

        await page.waitFor(2000);

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        await page.waitFor(2000);

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(2000);

        const departName = await page.$eval('.dept-list>li:last-child span', elem => {
            return elem.innerHTML;
        });
        await expect(departName).toEqual('部门三 (1人)');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();        

    });

    test('TEST_002:所有人不可见 组内成员登录' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'bumen3user', 'bumen3user');

        await page.waitFor(2000);

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(2000);

        const departName = await page.$eval('.dept-list>li:last-child span', elem => {
            return elem.innerHTML;
        });
        await expect(departName).toEqual('部门三 (1人)');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
        
    });

    test('TEST_003:所有人不可见 下属分组成员登录' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'mei6666', 'mei6666');

        await page.waitFor(2000);

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(2000);

        const departName = await page.$eval('.dept-list>li:last-child span', elem => {
            return elem.innerHTML;
        });
        await expect(departName).toEqual('部门三 (1人)');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
        
    });

})

describe('一账通-验证分组可见性-只对部分人可见', () => {
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);
       
    })
    afterAll ( async () => {

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    })

    test('TEST_001:只对部分人可见' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);

        const groupBtn2 = await page.waitForSelector('.ui-group-tree.ivu-tree>ul:nth-child(3) .ui-tree-item-bg');
        await groupBtn2.click();

        const editGroupBtn = await page.waitForSelector('.ui-group-page-detail-header.flex-row>button');
        await editGroupBtn.click();

        await page.waitFor(2000);

        const visibleBtn = await page.waitForSelector('div.ivu-drawer-wrap.ui-edit-group > div > div > div > form > div:nth-child(3) > div > div > div.ivu-select-selection');
        await visibleBtn.click();

        const visibleFive = await page.waitForSelector('div.ivu-drawer-wrap.ui-edit-group > div > div > div > form > div:nth-child(3) > div > div > div.ivu-select-dropdown > ul.ivu-select-dropdown-list > li:nth-child(5)');
        await visibleFive.click();

        await page.waitFor(2000);

        const filedBtn = await page.waitForSelector('div.ivu-drawer-wrap.ui-edit-group > div > div > div > form > div:nth-child(4) > div > div > textarea');
        await filedBtn.click();
        
        await page.waitFor(2000);

        const checkBox = await page.waitForSelector('div.ivu-modal-wrap.ui-choose-base > div > div > div.ivu-modal-body > div > div.ui-choose-base--middle > div > ul > li:nth-child(3) > label > span > input');
        await checkBox.click();

        const addBtn = await page.waitForSelector('div.ivu-modal-wrap.ui-choose-base > div > div > div.ivu-modal-footer > div > div > button.ivu-btn.ivu-btn-primary');
        await addBtn.click();

        await page.waitFor(2000);

        const keepBtn = await page.waitForSelector('.drawer-footer.flex-row.flex-auto>button:last-child');
        await keepBtn.click();

        await page.waitFor(2000);

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        await page.waitFor(2000);

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(2000);

        const departName = await page.$eval('.dept-list>li:last-child span', elem => {
            return elem.innerHTML;
        });
        await expect(departName).toEqual('部门三 (1人)');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();        

    });

    test('TEST_002:只对部分人可见 组内成员登录' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'bumen3user', 'bumen3user');

        await page.waitFor(2000);

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(2000);

        const departName = await page.$eval('.dept-list>li:last-child span', elem => {
            return elem.innerHTML;
        });
        await expect(departName).toEqual('部门三 (1人)');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
        
    });

    test('TEST_003:只对部分人可见 下属分组成员登录' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'mei6666', 'mei6666');

        await page.waitFor(2000);

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(2000);

        const departName = await page.$eval('.dept-list>li:last-child span', elem => {
            return elem.innerHTML;
        });
        await expect(departName).toEqual('部门三 (1人)');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
        
    });

    test('TEST_004:只对部分人可见 指定账号登录' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'mei222', 'mei222');

        await page.waitFor(2000);

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(2000);

        const departName = await page.$eval('.dept-list>li:last-child span', elem => {
            return elem.innerHTML;
        });
        await expect(departName).toEqual('部门三 (2人)');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
        
    });

})

describe('一账通-验证分组可见性-仅组内成员可见（下属分组不可见)下属分组为所有人不可见', () => {
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);
       
    })
    afterAll ( async () => {

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    })

    test('TEST_001:仅组内成员可见（下属分组不可见）' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);

        const groupBtn = await page.waitForSelector('div.ui-group-tree-component.tree > div.ui-group-tree-wrapper > div > ul:nth-child(3) > li > ul > li > div');
        await groupBtn.click();

        const editGroupBtn1 = await page.waitForSelector('.ui-group-page-detail-header.flex-row>button');
        await editGroupBtn1.click();

        await page.waitFor(2000);

        const visibleBtn1 = await page.waitForSelector('div.ivu-drawer-wrap.ui-edit-group > div > div > div > form > div:nth-child(3) > div > div > div.ivu-select-selection');
        await visibleBtn1.click();

        const visibleFour1 = await page.waitForSelector('div.ivu-drawer-wrap.ui-edit-group > div > div > div > form > div:nth-child(3) > div > div > div.ivu-select-dropdown > ul.ivu-select-dropdown-list > li:nth-child(4)');
        await visibleFour1.click();

        const keepBtn1 = await page.waitForSelector('.drawer-footer.flex-row.flex-auto>button:last-child');
        await keepBtn1.click();

        await page.waitFor(2000);

        const groupBtn2 = await page.waitForSelector('.ui-group-tree.ivu-tree>ul:nth-child(3) .ui-tree-item-bg');
        await groupBtn2.click();

        const editGroupBtn = await page.waitForSelector('.ui-group-page-detail-header.flex-row>button');
        await editGroupBtn.click();

        await page.waitFor(2000);

        const visibleBtn = await page.waitForSelector('div.ivu-drawer-wrap.ui-edit-group > div > div > div > form > div:nth-child(3) > div > div > div.ivu-select-selection');
        await visibleBtn.click();

        const visibleTwo = await page.waitForSelector('div.ivu-drawer-wrap.ui-edit-group > div > div > div > form > div:nth-child(3) > div > div > div.ivu-select-dropdown > ul.ivu-select-dropdown-list > li:nth-child(2)');
        await visibleTwo.click();

        const keepBtn = await page.waitForSelector('.drawer-footer.flex-row.flex-auto>button:last-child');
        await keepBtn.click();

        await page.waitFor(2000);

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        await page.waitFor(2000);

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(2000);

        const departName = await page.$eval('.dept-list>li:last-child span', elem => {
            return elem.innerHTML;
        });
        await expect(departName).toEqual('部门二 (0人)');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();        

    });

    test('TEST_002:仅组内成员可见（下属分组不可见）组内成员登录' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'bumen3user', 'bumen3user');

        await page.waitFor(2000);

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(2000);

        const departName = await page.$eval('.dept-list>li:last-child span', elem => {
            return elem.innerHTML;
        });
        await expect(departName).toEqual('部门三 (1人)');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
        
    });

    test('TEST_003:仅组内成员可见（下属分组不可见）下属分组成员登录' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'mei6666', 'mei6666');

        await page.waitFor(2000);

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(2000);

        const departName = await page.$eval('.dept-list>li:last-child span', elem => {
            return elem.innerHTML;
        });
        await expect(departName).toEqual('部门二 (0人)');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
        
    });

})

describe('一账通-验证分组可见性-组内成员及其下属分组可见', () => {
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);
       
    })
    afterAll ( async () => {

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    })

    test('TEST_001:组内成员及其下属分组可见' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);

        const groupBtn2 = await page.waitForSelector('.ui-group-tree.ivu-tree>ul:nth-child(3) .ui-tree-item-bg');
        await groupBtn2.click();

        const editGroupBtn = await page.waitForSelector('.ui-group-page-detail-header.flex-row>button');
        await editGroupBtn.click();

        await page.waitFor(2000);

        const visibleBtn = await page.waitForSelector('div.ivu-drawer-wrap.ui-edit-group > div > div > div > form > div:nth-child(3) > div > div > div.ivu-select-selection');
        await visibleBtn.click();

        const visibleThree = await page.waitForSelector('div.ivu-drawer-wrap.ui-edit-group > div > div > div > form > div:nth-child(3) > div > div > div.ivu-select-dropdown > ul.ivu-select-dropdown-list > li:nth-child(3)');
        await visibleThree.click();

        const keepBtn = await page.waitForSelector('.drawer-footer.flex-row.flex-auto>button:last-child');
        await keepBtn.click();

        await page.waitFor(2000);

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        await page.waitFor(2000);

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(2000);

        const departName = await page.$eval('.dept-list>li:last-child span', elem => {
            return elem.innerHTML;
        });
        await expect(departName).toEqual('部门二 (0人)');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();        

    });

    test('TEST_002:组内成员及其下属分组可见 组内成员登录' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'bumen3user', 'bumen3user');

        await page.waitFor(2000);

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(2000);

        const departName = await page.$eval('.dept-list>li:last-child span', elem => {
            return elem.innerHTML;
        });
        await expect(departName).toEqual('部门三 (1人)');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
        
    });

    test('TEST_003:组内成员及其下属分组可见 下属分组成员登录' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'mei6666', 'mei6666');

        await page.waitFor(2000);

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(2000);

        const departName = await page.$eval('.dept-list>li:last-child span', elem => {
            return elem.innerHTML;
        });
        await expect(departName).toEqual('部门三 (1人)');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
        
    });

})

describe('一账通-验证分组可见性-所有人不可见', () => {
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);
       
    })
    afterAll ( async () => {

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    })

    test('TEST_001:所有人不可见' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);

        const groupBtn2 = await page.waitForSelector('.ui-group-tree.ivu-tree>ul:nth-child(3) .ui-tree-item-bg');
        await groupBtn2.click();

        const editGroupBtn = await page.waitForSelector('.ui-group-page-detail-header.flex-row>button');
        await editGroupBtn.click();

        await page.waitFor(2000);

        const visibleBtn = await page.waitForSelector('div.ivu-drawer-wrap.ui-edit-group > div > div > div > form > div:nth-child(3) > div > div > div.ivu-select-selection');
        await visibleBtn.click();

        const visibleFour = await page.waitForSelector('div.ivu-drawer-wrap.ui-edit-group > div > div > div > form > div:nth-child(3) > div > div > div.ivu-select-dropdown > ul.ivu-select-dropdown-list > li:nth-child(4)');
        await visibleFour.click();

        const keepBtn = await page.waitForSelector('.drawer-footer.flex-row.flex-auto>button:last-child');
        await keepBtn.click();

        await page.waitFor(2000);

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        await page.waitFor(2000);

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(2000);

        const departName = await page.$eval('.dept-list>li:last-child span', elem => {
            return elem.innerHTML;
        });
        await expect(departName).toEqual('部门二 (0人)');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();        

    });

    test('TEST_002:所有人不可见 组内成员登录' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'bumen3user', 'bumen3user');

        await page.waitFor(2000);

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(2000);

        const departName = await page.$eval('.dept-list>li:last-child span', elem => {
            return elem.innerHTML;
        });
        await expect(departName).toEqual('部门二 (0人)');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
        
    });

    test('TEST_003:所有人不可见 下属分组成员登录' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'mei6666', 'mei6666');

        await page.waitFor(2000);

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(2000);

        const departName = await page.$eval('.dept-list>li:last-child span', elem => {
            return elem.innerHTML;
        });
        await expect(departName).toEqual('部门二 (0人)');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
        
    });

})

describe('一账通-验证分组可见性-只对部分人可见', () => {
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);
       
    })
    afterAll ( async () => {

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    })

    test('TEST_001:只对部分人可见' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);

        const groupBtn2 = await page.waitForSelector('.ui-group-tree.ivu-tree>ul:nth-child(3) .ui-tree-item-bg');
        await groupBtn2.click();

        const editGroupBtn = await page.waitForSelector('.ui-group-page-detail-header.flex-row>button');
        await editGroupBtn.click();

        await page.waitFor(2000);

        const visibleBtn = await page.waitForSelector('div.ivu-drawer-wrap.ui-edit-group > div > div > div > form > div:nth-child(3) > div > div > div.ivu-select-selection');
        await visibleBtn.click();

        const visibleFive = await page.waitForSelector('div.ivu-drawer-wrap.ui-edit-group > div > div > div > form > div:nth-child(3) > div > div > div.ivu-select-dropdown > ul.ivu-select-dropdown-list > li:nth-child(5)');
        await visibleFive.click();

        await page.waitFor(2000);

        const keepBtn = await page.waitForSelector('.drawer-footer.flex-row.flex-auto>button:last-child');
        await keepBtn.click();

        await page.waitFor(2000);

        const returnDeskBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await returnDeskBtn.click();

        await page.waitFor(2000);

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(2000);

        const departName = await page.$eval('.dept-list>li:last-child span', elem => {
            return elem.innerHTML;
        });
        await expect(departName).toEqual('部门二 (0人)');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();        

    });

    test('TEST_002:只对部分人可见 组内成员登录' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'bumen3user', 'bumen3user');

        await page.waitFor(2000);

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(2000);

        const departName = await page.$eval('.dept-list>li:last-child span', elem => {
            return elem.innerHTML;
        });
        await expect(departName).toEqual('部门二 (0人)');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
        
    });

    test('TEST_003:只对部分人可见 下属分组成员登录' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'mei6666', 'mei6666');

        await page.waitFor(2000);

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(2000);

        const departName = await page.$eval('.dept-list>li:last-child span', elem => {
            return elem.innerHTML;
        });
        await expect(departName).toEqual('部门二 (0人)');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
        
    });

    test('TEST_003:只对部分人可见 指定账号登录' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'mei222', 'mei222');

        await page.waitFor(2000);

        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();

        await page.waitFor(2000);

        const departName = await page.$eval('.dept-list>li:last-child span', elem => {
            return elem.innerHTML;
        });
        await expect(departName).toEqual('部门三 (1人)');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
        
    });

})

describe('一账通-分组管理编辑部门的权限', () => {
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

    })
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
       
    });

})

describe('一账通-分组管理编辑部门的权限', () => {
    let page : Page;

    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

    })
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_002:验证修改权限后是否生效' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'mei123', 'meixinyue');

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
        
    });

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

    })
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
       
    });

})

describe('一账通-分组管理自定义分组的权限', () => {
    let page : Page;

    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

    })
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
        
    });

})