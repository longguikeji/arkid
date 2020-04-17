import { UserAction } from './actions/user';
import {Page, launch} from 'puppeteer';
import {accountAction} from './actions/account';
import config from './config';
import expectPuppeteer = require('expect-puppeteer');

declare var global: any

describe('一账通-账号管理测试', () => {
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

    },90000)
    afterEach ( async () => {
       
    })

    test('TEST_001:验证账号管理页面链接' , async() => {
        await page.waitFor(2000);
        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');
        
        await page.waitFor(2000);

        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        await page.waitFor(2000);

        //const accountBtn = await page.waitForSelector('a[href="#/workspace/account"]');
        //await accountBtn.click();

        //await page.waitFor(5000);

        const url = await page.url();
        await expect(url).toMatch('admin/account');
     
        await page.close();
    },30000);
    
    test('TEST_002:验证账号管理页面添加新账号' , async() => {
        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');
        
        await page.waitFor(5000);

        let accountaction = new accountAction();
        await accountaction.addAccount(page, "mxyzz",  "meixinyue", "mei123456", "mei123456", "15822186268", "1821788073@qq.com", "meixinyue11@163.com");         

        page = await global.browser.newPage()
        await page.goto(config.url);

        await useraction.login(page, 'admin', 'admin'); 

        //const manageBtn2 = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        //await manageBtn2.click();

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

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });

        await page.close();
    },50000);

    test('TEST_003:验证账号管理页面添加的新账号能否登录' , async() => {
       // page = await global.browser.newPage()
       // await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'mxyzz', 'mei123456'); 

        console.log("mxyzz login");
        await page.waitFor(2000);
        console.log(page.url());

        const url = await page.url();
        await expect(url).toMatch('#/workspace/apps');
  
        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();      
    },40000);
})

describe('一账通-账号管理搜索账号', () => {
    let page : Page;
    
    beforeEach( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        await page.waitFor(1000);

        let accountaction = new accountAction();
        await accountaction.searchAccount(page, "mei111");          

    },30000)
    afterAll ( async () => {
        
    })

    test('TEST_001:验证账号管理的搜索框' , async() => {
        const name = await page.$eval('.ivu-table-body.ivu-table-overflowX > table > tbody > tr > td:nth-child(2) > div > span:nth-child(1)', elem => {
            return elem.innerHTML;
        });
        await expect(name).toEqual('mei111');
        
        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });

        await page.close();
    },30000);

})

describe('一账通-账号管理编辑账号', () => {
    let page : Page;
    
    beforeAll( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

    },100000)
    afterEach ( async () => {
       
    })

    test('TEST_001:验证修改是否生效' , async() => {

        let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

          const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
          await manageBtn.click();

        let accountaction = new accountAction();
        await accountaction.searchAccount(page, "mei222");
        await accountaction.reviseAccount(page, "11", "meixinyue", "meixinyue");

        await page.waitFor(2000);

        const name = await page.$eval('.ivu-table-row>td:nth-child(3) span', elem => {
            return elem.innerHTML;
        });
        await expect(name).toEqual('mei22211');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();

    },50000);

    test('TEST_002:验证修改密码后能否登录' , async() => {
        page = await global.browser.newPage()
        await page.goto(config.url);

        let useraction = new UserAction();
        await useraction.login(page, 'mei222', 'meixinyue');

        await page.waitFor(6000);
        const url = await page.url();
        await expect(url).toMatch('#/workspace/apps');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close(); 
        
    },40000);
})

describe('一账通-账号管理删除账号', () => {
    let page : Page;
    
    beforeAll( async () => {
        page = await global.browser.newPage()
        await page.goto(config.url);

    },60000)
    afterAll ( async () => {
       
    })

    test('TEST_001:验证删除账号' , async() => {
       let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        await page.waitFor(1000);
   
        let accountaction = new accountAction();
        await accountaction.searchAccount(page, "bumen3user");
        console.log("search bumen3user");

        await accountaction.deleteAccount(page);

        await page.waitFor(5000);
      
        page = await global.browser.newPage()
        await page.goto(config.url);

        //let useraction = new UserAction();
        await useraction.login(page, 'admin', 'admin');

        //const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
       // await manageBtn.click();

        await page.waitFor(3000);

        const userName = await page.$eval('.ivu-table-tbody>tr:first-child>td:nth-child(2) span', elem => {
            return elem.innerHTML;
        });
        await expect(userName).toEqual('mei111');

        await page.evaluate(() => {
            localStorage.setItem('oneid', '');
        });
        await page.close();        
    },60000);

})

