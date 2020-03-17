import {Page, launch} from 'puppeteer';

 
export class appMessageAction{
    public async appinformation(page:Page){
        const deskBtn = await page.waitForSelector('.ivu-menu-item.ivu-menu-item-active.ivu-menu-item-selected');
        deskBtn.click();
        await page.waitFor(3000);
        await page.waitForSelector('.card-list.flex-row>li',{timeout:10000});
        const apps = await page.$$('.card-list.flex-row>li');
        const appsVal = await page.$$eval('.card-list.flex-row>li',eles=>(eles.map(ele=>ele.textContent)));
        console.log('apps ==',appsVal);
    }
}