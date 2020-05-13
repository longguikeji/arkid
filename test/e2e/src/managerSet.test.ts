import { UserAction } from './actions/user';
import {Page, launch} from 'puppeteer';
import config from './config';
import expectPuppeteer = require('expect-puppeteer');
import {groupAction} from './actions/group';
import {configManageAction} from './actions/configManage';
import {appsManageAction} from './actions/appsManage';
import {managerSettingAction} from './actions/managerSetting';

declare var global: any

jest.setTimeout(600000);

describe('一账通-测试设置子管理员', () => {
    let page : Page;
    
    beforeEach( async () => {

        page = await global.browser.newPage()
        await page.goto(config.url);
        
    })
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证设置子管理员页面链接' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        await page.waitFor(5000);

        const managerBtn = await page.waitForSelector('body > div.lg-layout > header > div.header-middle > ul > a:nth-child(5)');
        await managerBtn.click();

        await page.waitFor(3000);

        const url = await page.url();
        await expect(url).toMatch('#/admin/manager');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
        
    });

    test('TEST_002:验证设置子管理员是否生效' , async() => {//所在分组及下级分组，未分配权限
        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        await page.waitFor(2000);

        const managerBtn = await page.waitForSelector('a[href="#/admin/manager"]');
        await managerBtn.click();

        await page.waitFor(3000);
        
        let managersettingaction = new managerSettingAction();
        await managersettingaction.managerSetting(page);//添加子管理员
        
        const managerName = await page.$eval('.ivu-table-tbody>tr:last-child .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(managerName).toEqual('mei111');//是否成功添加到子管理员列表

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
    });

})

describe('一账通-测试设置子管理员a', () => {//管理范围所在分组及下级分组，创建用户
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

    })
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证设置子管理员是否生效' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let managersettingaction = new managerSettingAction();
        await managersettingaction.managerSettinga(page);//添加子管理员

        await page.waitFor(3000);

        const managerName = await page.$eval('.ivu-table-tbody>tr:last-child .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(managerName).toEqual('bumen3user');//是否成功添加到子管理员列表
   
        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
        
    });

    test('TEST_001:验证设置子管理员添加账号是否生效' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'bumen3user', 'bumen3user');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.addUser(page, "mei111add", "mei111add", "mei111add", "mei111add");//子管理员添加账号
        
        const userName = await page.$eval('.ivu-table-tbody>tr:last-child>td:nth-child(2)>div>span', elem => {
            return elem.innerHTML;
        });
        await expect(userName).toEqual('mei111add');//是否添加成功

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
    });

    test('TEST_002:验证设置子管理员添加的账号能否登录' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'mei111add', 'mei111add');//子管理员添加账号是否能登录

        await page.waitFor(2000);
        
        const url = await page.url();
        await expect(url).toMatch('workspace/apps');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
    });

})

describe('一账通-测试设置子管理员b', () => {//所在分组及下级分组，创建应用，查看日志
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

    })
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证设置子管理员是否生效' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let managersettingaction = new managerSettingAction();
        await managersettingaction.managerSettingb(page);//添加子管理员

        await page.waitFor(3000);

        const managerName = await page.$eval('.ivu-table-tbody>tr:last-child .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(managerName).toEqual('mei222');//是否成功添加到子管理员列表

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
    });

    test('TEST_002:验证设置子管理员添加应用是否生效' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'mei222', 'mei222');

        let appsmanageaction = new appsManageAction();
        await appsmanageaction.addApps(page, "测试应用", "", "ceshiyingyong");//创建应用

        await page.waitFor(3000);

        const appName = await page.$eval('.ivu-table-tbody>tr:last-child>td:nth-child(2) .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(appName).toEqual('测试应用');//是否成功添加应用到应用列表

        const remarks = await page.$eval('.ivu-table-tbody>tr:last-child>td:nth-child(3) .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(remarks).toEqual('ceshiyingyong');//应用备注

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
    });


    test('TEST_003:验证设置子管理员查看日志' , async() => {//查看日志
        let useraction = new UserAction();
        await useraction.login(page, 'mei222', 'mei222');

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

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
    });

})

describe('一账通-测试设置子管理员c', () => {//所在分组及下级分组公司基础信息配置
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

    })
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证设置子管理员是否成功' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');
       
        let managersettingaction  = new managerSettingAction();
        await managersettingaction.managerSettingc(page);//添加子管理员

        await page.waitFor(3000);

        const managerName = await page.$eval('.ivu-table-tbody>tr:last-child .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(managerName).toEqual('mei333');//是否添加到子管理员列表

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    });

    test('TEST_002:验证设置子管理员公司信息配置' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'mei333', 'mei333');
 
        let configmanageaction = new configManageAction();
        await configmanageaction.loginSetting(page, "111");//修改公司配置信息

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

        page = await global.browser.newPage()
        await page.goto(config.url);

        //let useraction = new UserAction();
        await useraction.login(page, 'mei333', 'mei333');

        const companyName = await page.$eval('.org-name', elem => {
            return elem.innerHTML;
        });
        await expect(companyName).toEqual('111');//是否修改成功

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
    });

})

describe('一账通-测试设置子管理员d', () => {//所在分组及下级分组应用百度应用权限
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

    })
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证设置子管理员应用权限' , async() => {//成功添加子管理员
        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');
        let managersettingaction = new managerSettingAction();
        await managersettingaction.managerSettingd(page); 

        await page.waitFor(3000);

        const managerName = await page.$eval('.ivu-table-tbody>tr:last-child .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(managerName).toEqual('axiangmuzuuser');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    });

    test('TEST_002:验证设置子管理员应用权限-修改应用信息' , async() => {//修改应用信息

        let useraction = new UserAction();
        await useraction.login(page, 'axiangmuzuuser', 'axiangmuzuuser');

        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        await page.waitFor(2000);

        const appSetBtn = await page.waitForSelector('.header-middle a[href="#/admin/app"]');
        await appSetBtn.click();

        await page.waitFor(3000);

        const appName1 = await page.$eval('.ivu-table-row>td:nth-child(2) span', elem => {
            return elem.innerHTML;
        });
        await expect(appName1).toEqual('百度');

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
        await expect(appName2).toEqual('百度111');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    });

    test('TEST_003:验证设置子管理员应用权限-编辑应用权限-只显示可管理账号' , async() => {

        let useraction = new UserAction();
        await useraction.login(page, 'axiangmuzuuser', 'axiangmuzuuser');

        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        await page.waitFor(2000);

        const appSetBtn = await page.waitForSelector('.header-middle a[href="#/admin/app"]');
        await appSetBtn.click();

        await page.waitFor(3000);

        const powerBtn = await page.waitForSelector('.ivu-table-row .flex-row>span:nth-child(3)');
        await powerBtn.click();

        await page.waitFor(2000);

        const editBtn = await page.waitForSelector('div.ivu-table-body.ivu-table-overflowX > table > tbody > tr > td:nth-child(3) > div > div > span');
        await editBtn.click();

        await page.waitFor(3000);

        const userName1 = await page.$eval('.ivu-cell-group>div .ivu-cell-title span', elem => {
            return elem.innerHTML;
        });
        await expect(userName1).toEqual('axiangmuzuuser');//可添加到白名单的账号列表只有有权管理的账号

        const userName2 = await page.$eval('.ivu-cell-group>div:last-child .ivu-cell-title span', elem => {
            return elem.innerHTML;
        });
        await expect(userName2).toEqual('axiangmuzuuser');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    });

    test('TEST_004:验证设置子管理员应用权限-编辑应用权限-添加账号到白名单' , async() => {

        let useraction = new UserAction();
        await useraction.login(page, 'axiangmuzuuser', 'axiangmuzuuser');

        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        await page.waitFor(2000);

        const appSetBtn = await page.waitForSelector('.header-middle a[href="#/admin/app"]');
        await appSetBtn.click();

        await page.waitFor(3000);

        const powerBtn = await page.waitForSelector('.ivu-table-row .flex-row>span:nth-child(3)');
        await powerBtn.click();

        await page.waitFor(2000);

        const editBtn = await page.waitForSelector('div.ivu-table-body.ivu-table-overflowX > table > tbody > tr > td:nth-child(3) > div > div > span');
        await editBtn.click();

        await page.waitFor(3000);

        const userCheckbox = await page.waitForSelector('div.ivu-checkbox-group.ivu-checkbox-default > div > div> div > div > div.ivu-cell-main > div.ivu-cell-title > label > span.ivu-checkbox > input');
        await userCheckbox.click();

        await page.waitFor(1000);

        const keepBtn = await page.waitForSelector('div.ivu-modal-footer > button.ivu-btn.ivu-btn-primary.ivu-btn-large');
        await keepBtn.clcik();

        await page.waitFor(2000);

        const userName = await page.$eval('div.ivu-table-body.ivu-table-overflowX > table > tbody > tr > td:nth-child(3) > div > div > div > div > span', elem => {
            return elem.innerHTML;
        });
        await expect(userName).toEqual('axiangmuzuuser');//成功添加账号到白名单

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    });

    test('TEST_005:验证设置子管理员应用权限-编辑应用权限-账号是否生效' , async() => {

        let useraction = new UserAction();
        await useraction.login(page, 'axiangmuzuuser', 'axiangmuzuuser');//白名单的账号登录查看权限是否生效

        await page.waitFor(2000);

        const appName = await page.$eval('.name-intro.flex-col.flex-auto .name', elem => {
            return elem.innerHTML;
        });
        await expect(appName).toEqual('百度');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    });

})

describe('一账通-测试编辑子管理员', () => {//编辑子管理员axiangmuzuuser
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let managersettingaction = new managerSettingAction();
        await managersettingaction.editManager(page);//调用编辑函数，添加查看日志权限

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    })
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证编辑子管理员权限' , async() => {//验证添加查看日志权限是否生效
        page = await global.browser.newPage()
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

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    });

})

describe('一账通-测试删除子管理员', () => {//删除子管理员axiangmuzuuser
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let managersettingaction = new managerSettingAction();
        await managersettingaction.deleteManager(page);

    })
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证删除子管理员' , async() => {//验证删除是否生效

        const managerName = await page.$eval('.ivu-table-tbody>tr:last-child .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(managerName).toEqual('mei333');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close()

    });

})

describe('一账通-测试设置子管理员e', () => {//管理范围所在分组及下级分组，创建大类
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

    })
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证设置子管理员是否生效' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let managersettingaction = new managerSettingAction();
        await managersettingaction.managerSettinge(page);

        await page.waitFor(3000);

        const managerName = await page.$eval('.ivu-table-tbody>tr:last-child .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(managerName).toEqual('bumen3user');//添加子管理员到列表
   
        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
        
    });

    test('TEST_001:验证设置子管理员创建大类是否生效' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'bumen3user', 'bumen3user');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page);
        await groupaction.addPersonalGroup(page, "bumen3useradd");
        
        const classifyName = await page.$eval('.custom-list>li:last-child span', elem => {
            return elem.innerHTML;
        });
        await expect(classifyName).toEqual('bumen3useradd');//子管理员创建大类在分组管理是否生效

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
    });

    test('TEST_002:验证设置子管理员创建的大类在通讯录是否生效' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        await page.waitFor(2000);

        const orgnizationBtn = await page.waitForSelector('body > div.lg-layout > header > div.header-middle > ul > a:nth-child(2)');
        await orgnizationBtn.click();
        
        const classifyName = await page.$eval('.ui-contact-page--side>li:last-child', elem => {
            return elem.innerHTML;
        });
        await expect(classifyName).toEqual('bumen3useradd');//子管理员创建大类在通讯录是否生效

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
    });

})

describe('一账通-测试设置子管理员f', () => {//管理范围所在分组及下级分组，应用百度的权限
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

    })
    afterAll ( async () => {
        //await page.close();
    })

    test('TEST_001:验证设置子管理员是否生效' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        let managersettingaction = new managerSettingAction();
        await managersettingaction.managerSettinge(page);

        await page.waitFor(3000);

        const managerName = await page.$eval('.ivu-table-tbody>tr:last-child .ivu-table-cell span', elem => {
            return elem.innerHTML;
        });
        await expect(managerName).toEqual('bumen3user');
   
        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
        
    });

    test('TEST_001:设置子管理员应用的权限-部门' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'bumen3user', 'bumen3user');
 
        let appsmanageaction = new appsManageAction();
        await appsmanageaction.departmentPower(page, "部门三");
        
        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
    });

    test('TEST_002:验证设置子管理员应用的权限-部门是否生效' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'bumen3user', 'bumen3user');

        await page.waitFor(3000);
        
        const appName = await page.$eval('.name-intro.flex-col.flex-auto .name', elem => {
            return elem.innerHTML;
        });
        await expect(appName).toEqual('百度');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
    });
    
    test('TEST_003:验证设置子管理员分组管理权限只显示可管理的应用' , async() => {//子管理员查看可管理分组的权限
        let useraction = new UserAction();
        await useraction.login(page, 'bumen3user', 'bumen3user');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page); 
        
        await page.waitFor(2000);
        
        const powerBtn = await page.waitForSelector('.ivu-btn.ivu-btn-primary');
        await powerBtn.click();

        await page.waitFor(2000);

        const appName1 = await page.$eval('.result-list>li span', elem => {
            return elem.innerHTML;
        });
        await expect(appName1).toEqual('百度');//应用列表第一个应用的名称

        const appName2 = await page.$eval('.result-list>li:last-child span', elem => {
            return elem.innerHTML;
        });
        await expect(appName2).toEqual('百度');//应用列表最后一个应用的名称

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
    });

    test('TEST_003:验证设置子管理员编辑分组管理权限' , async() => {//子管理员编辑分组对应用的权限
        let useraction = new UserAction();
        await useraction.login(page, 'bumen3user', 'bumen3user');

        let groupaction = new groupAction();
        await groupaction.groupAddress(page); 
        
        await page.waitFor(2000);
        
        const powerBtn = await page.waitForSelector('.ivu-btn.ivu-btn-primary');
        await powerBtn.click();

        await page.waitFor(2000);

        const editPowerBtn = await page.waitForSelector('div.ivu-table-body > table > tbody > tr > td:nth-child(3) > div > div > div > div');
        await editPowerBtn.click();

        await page.waitFor(1000);

        const falseBtn = await page.waitForSelector('div.ivu-select-dropdown.ivu-dropdown-transfer > ul > li:nth-child(2)');//将分组对百度应用的权限设置为否
        await falseBtn.click();

        await page.waitFor(2000);

        const powerResult = await page.$eval('div.ivu-table-body > table > tbody > tr > td:nth-child(4) > div > span', elem => {
            return elem.innerHTML;
        });
        await expect(powerResult).toEqual('否');//权限结果变为否

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();
    });

})

