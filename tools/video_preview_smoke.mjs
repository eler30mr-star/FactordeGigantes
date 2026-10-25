// Read-only acceptance of the existing development artifact; never renders.
import {readFileSync} from 'node:fs';
import {extractPreview} from '../public/video-preview.js';
const archive=readFileSync(process.argv[2]);
const blob=await extractPreview(archive,{
 archiveHash:'b4f68867dd3989776b08b2af756b59bfb40b67f3755e9f7704c34ee6fc8df4bd',
 videoHash:'398d5963d25f35f2c1bccb2b7c759e25ec224758243d99e250bccf000f3991ad',videoBytes:30308212
});
console.log(JSON.stringify({archive_verified:true,video_verified:true,video_bytes:blob.size,
 content_type:blob.type,generated_models:0,publication_authorized:false}));
