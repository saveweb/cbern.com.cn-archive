// Author: @baoshuo

const fs = require('fs');
const fetch = require('node-fetch');

const urls = [
    'https://s-file-2.ykt.cbern.com.cn/zxx/ndrs/resources/tch_material/part_100.json',
    'https://s-file-2.ykt.cbern.com.cn/zxx/ndrs/resources/tch_material/part_101.json',
    'https://s-file-2.ykt.cbern.com.cn/zxx/ndrs/resources/tch_material/part_102.json',
];

const promises = urls.map((url) => fetch(url).then((res) => res.json()));

Promise.all(promises).then(async (data) => {
    let cur = 0;
    const result = data.reduce((acc, cur) => {
        return acc.concat(cur);
    }, []);
    let str = '';

    for (const item of result) {
        if (item.tag_paths.length <= 0) continue;

        const tags = item.tag_paths[0]
            .split('/')
            .map(
                (id) => item.tag_list.find((tag) => tag.tag_id === id).tag_name
            );

        const dir = tags.join('/');

        str += `https://r2-ndr.ykt.cbern.com.cn/edu_product/esp/assets_document/${
            item.id
        }.pkg/pdf.pdf\n  out=${dir + '/' + item.title + '.pdf'}\n`;

        // fs.mkdirSync(dir, { recursive: true });

        // let try_cnt = 0;

        // while (++try_cnt < 10) {
        //     try {
        //         const res = fetch(
        //             'https://r2-ndr.ykt.cbern.com.cn/edu_product/esp/assets_document/' +
        //                 item.id +
        //                 '.pkg/pdf.pdf'
        //         );
        //         const stream = fs.createWriteStream(
        //             dir + '/' + item.title + '.pdf'
        //         );

        //         await res.then((res) => res.body.pipe(stream));

        //         console.log(
        //             'SUCCESS',
        //             `${++cur}/${result.length} (${try_cnt})`,
        //             item.id,
        //             dir + '/' + item.title + '.pdf'
        //         );

        //         break;
        //     } catch (e) {
        //         console.log('ERROR', item.id, dir + '/' + item.title + '.pdf');
        //     }
        // }
    }

    fs.writeFileSync('temp_result.txt', str);
});
