import fetch from 'dva/fetch';

export async function generate_tts(task){
  let response=await fetch('/tts/generate',{
    headers: {
      "Content-Type": "application/json"
    },
    method: 'POST',
    body: JSON.stringify(task)
  });
  return await response.json();
}
