import {UserAction} from './actions/user'
import {Page, launch} from 'puppeteer';
import {deskAction} from './actions/desk';
import {organizationAction} from './actions/organization';
import {setAction} from './actions/setting';
import {accountAction} from './actions/account';

async function run(){
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

run();