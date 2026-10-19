export type User = {id:number;username:string;email:string;bio:string;location:string;skills:string[];github_url:string;linkedin_url:string;portfolio_url:string;is_staff?:boolean};
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
export async function list<T>(path:string):Promise<T[]>{
  const all:T[]=[];
  let next:string|null='/api/'+path.replace(/^\//,'');
  let pages=0;
  while(next && pages<100){
    // DRF pagination produces URLs; require them to remain on the same origin and under /api/.
    const url:URL=new URL(next,window.location.origin);
    if(url.hostname!==window.location.hostname || !url.pathname.startsWith('/api/')) throw new Error('Lien de pagination invalide');
    const result=await request<List<T>|T[]>(url.pathname.slice(5)+url.search);
    if(Array.isArray(result)){all.push(...result);break;}
    all.push(...result.results);
    next=result.next;
    pages++;
  }
  return all;
}

