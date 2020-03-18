import {Page, launch} from 'puppeteer';
    export class organizationAction{
        public async origanization(page:Page){
            
            const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
            await orgBtn.click();
            page.waitFor(3000);

            // const groups = await page.$$('.lg-layout--body .ui-contact-page--side>li');
            
            // for (let i = 1; i < 5; i++) {
            //     const button = groups[i]

            //     await button.click();
            //     const orgInput = await page.waitForSelector('.ivu-input.ivu-input-default.ivu-input-with-suffix');
            //     await orgInput.type(searchOrg);

            // }

            // for (let i = 6; i < groups.length; i++) {
            //     const button = groups[i]

            //     await button.click();
            //     const orgInput = await page.waitForSelector('.ivu-input.ivu-input-default.ivu-input-with-suffix');
            //     await orgInput.type(searchOrg);
                
            // }

        } 
    }