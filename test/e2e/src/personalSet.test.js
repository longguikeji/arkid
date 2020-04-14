const puppeteer = require('puppeteer');
  
test('一账通-退出登录', async () => {
    const browser = await puppeteer.launch();
    page = await browser.newPage();
    await page.goto('http://192.168.200.115:8989');

    const usernameInput = await page.waitForSelector('input[type = "text"]');
    await usernameInput.type("admin");
    const passwordInput = await page.waitForSelector('input[type = "password"]');
    await passwordInput.type("admin");
        
    const loginBtn = await page.waitForSelector('button[type = "button"]');
    await loginBtn.click();

    await page.waitFor(4000);

    const settingBtn = await page.waitForSelector('.ivu-icon.ivu-icon-md-arrow-dropdown');
    await settingBtn.click();

    await page.evaluate(()=> {
        document.querySelector('.ivu-dropdown-menu>li').click()
    });
    await page.waitFor(3000);

    const url = await page.url();
    await expect(url).toMatch('#/oneid/login?backPath=%2Fworkspace%2Fapps');
},30000);

test('一账通-修改密码', async () => {
    const browser = await puppeteer.launch({headless:false});
    page = await browser.newPage();
    await page.goto('http://192.168.200.115:8989');

    const usernameInput = await page.waitForSelector('input[type = "text"]');
    await usernameInput.type("bxiangmuzuuser");
    const passwordInput = await page.waitForSelector('input[type = "password"]');
    await passwordInput.type("bxiangmuzuuser");
        
    const loginBtn = await page.waitForSelector('button[type = "button"]');
    await loginBtn.click();

    await page.waitFor(4000);

    const settingBtn = await page.waitForSelector('body > div.lg-layout > header > div.header-right > div');
    await settingBtn.click();

    await page.evaluate(()=> {
        document.querySelector('.ivu-dropdown-menu>li:nth-child(2)').click()
    });
    await page.waitFor(3000);

    const oldPwdInput = await page.waitForSelector('input[placeholder="输入原密码"]');
    await oldPwdInput.type("bxiangmuzuuser");

    await page.waitFor(1000);

    const newPwdInput = await page.waitForSelector('input[placeholder="输入新密码"]');
    await newPwdInput.type("bxiangmuzu111");

    await page.waitFor(1000);

    const renewPwdInput = await page.waitForSelector('input[placeholder="再次输入新密码"]');
    await renewPwdInput.type("bxiangmuzu111");

    await page.waitFor(1000);

    const defineBtn = await page.waitForSelector('.right-button.ivu-btn.ivu-btn-primary');
    await defineBtn.click();

    await page.waitFor(3000);

    const usernameInput1 = await page.waitForSelector('input[type = "text"]');
    await usernameInput1.type("bxiangmuzuuser");
    const passwordInput1 = await page.waitForSelector('input[type = "password"]');
    await passwordInput1.type("bxiangmuzu111");
        
    const loginBtn1 = await page.waitForSelector('button[type = "button"]');
    await loginBtn1.click();

    await page.waitFor(3000);

    const url = await page.url();
    await expect(url).toMatch('#/workspace/apps');
},50000);

