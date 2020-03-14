import {UserAction} from './actions/user'
import {Page, launch} from 'puppeteer';
import {deskAction} from './actions/desk';
import {organizationAction} from './actions/organization';
import {setAction} from './actions/setting';

async function run(){
    let browser = await launch({headless:false, defaultViewport:{width:1366,height:768}})
    let page:Page = await browser.newPage();
    let useraction = new UserAction();
    let deskaction = new deskAction();
    let organizationaction = new organizationAction();
    let setaction = new setAction();
    

    await useraction.login(page, 'admin', 'longguikeji');

    await page.goto('https://arkid.demo.longguikeji.com/#/workspace/apps');

    await deskaction.appinformation(page, '街道');

    await organizationaction.origanization(page, "111");

    await setaction.setting(page, "abc");





}

run();