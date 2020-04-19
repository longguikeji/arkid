import {Page, launch} from 'puppeteer';

export class appMessageAction{
    public async appinformation(page:Page){
       // const returnBtn = await page.waitForSelector('body > div.lg-layout > header > div.header-right > a:nth-child(1) > button');
       // await returnBtn.click();

        //const deskBtn = await page.waitForSelector('a[href="#/workspace/apps"]');
       // deskBtn.click();
        await page.waitFor(3000);
        await page.waitForSelector('.card-list.flex-row>li');
        const apps = await page.$$('.card-list.flex-row>li');
        const appsVal = await page.$$eval('.card-list.flex-row>li',eles=>(eles.map(ele=>ele.textContent)));
        console.log('apps ==',appsVal);
    }
}
