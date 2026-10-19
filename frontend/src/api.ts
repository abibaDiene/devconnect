export type User = {id:number;username:string;email:string;bio:string;location:string;skills:string[];github_url:string;linkedin_url:string;portfolio_url:string};
export type Post = {id:number;author:number;content:string;created_at:string;comments_count:number;reactions_count:number};
export type Question = {id:number;author:number;title:string;body:string;tags:string[];accepted_answer:number|null;created_at:string};
export type Project = {id:number;owner:number;name:string;description:string;technologies:string[];github_url:string;demo_url:string;seeking_collaborators:boolean;created_at:string};
type List<T> = {results:T[];count:number;next:string|null};
const cookie = (name:string) => document.cookie.split('; ').find(p=>p.startsWith(name+'='))?.slice(name.length+1);
function detail(data:unknown):string {if(typeof data==='string')return data;if(data&&typeof data==='object'){const obj=data as Record<string,unknown>;return Object.entries(obj).map(([k,v])=>`${k}: ${Array.isArray(v)?v.join(', '):String(v)}`).join(' · ')}return 'Erreur inattendue';}
export async function request<T>(path:string,method='GET',body?:unknown):Promise<T>{
  if(method!=='GET' && !cookie('csrftoken')) await fetch('/api/auth/csrf/',{credentials:'include'});
  const response=await fetch('/api/'+path.replace(/^\//,''),{method,credentials:'include',headers:{...(body!==undefined?{'Content-Type':'application/json'}:{}),...(method!=='GET'?{'X-CSRFToken':decodeURIComponent(cookie('csrftoken')||'')}: {})},...(body!==undefined?{body:JSON.stringify(body)}:{})});
  if(!response.ok){let data:unknown;try{data=await response.json()}catch{data='Impossible de contacter le serveur.'}throw new Error(detail(data));}
  if(response.status===204)return undefined as T;
  return response.json() as Promise<T>;
}
export async function list<T>(path:string):Promise<T[]>{const result=await request<List<T>|T[]>(path);return Array.isArray(result)?result:result.results;}
