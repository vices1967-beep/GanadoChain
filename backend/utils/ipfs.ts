import { create } from "ipfs-http-client";

const projectId = process.env.IPFS_PROJECT_ID || "";
const projectSecret = process.env.IPFS_PROJECT_SECRET || "";
const auth = 'Basic ' + Buffer.from(projectId + ':' + projectSecret).toString('base64');

export const ipfs = create({
  host: 'ipfs.infura.io',
  port: 5001,
  protocol: 'https',
  headers: {
    authorization: auth,
  },
});

export async function uploadJson(json: object) {
  const { path } = await ipfs.add(JSON.stringify(json));
  return path; // Hash CID
}
