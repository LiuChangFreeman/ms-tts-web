import React, {useEffect, useRef, useState} from "react";
import {generate_tts} from "../services/services";
import {
  TextField, Stack, Text, Slider, DropdownMenuItemType, Dropdown,
  DefaultButton, PrimaryButton, Spinner
} from "office-ui-fabric-react";
import {Toast} from "antd-mobile";
import {ttsStyles} from "../assets/resources";
import {formatDate, isNotMobile} from "../utils/utils";
import Player from "griffith";

const TtsGenerator= (props) => {
  const [text,setText]=useState("");
  const [rate,setRate]=useState(10);
  const [style,setStyle]=useState("Default");
  const [styleDesc,setStyleDesc]=useState("默认值");
  const [loading,setLoading]=useState(false);
  const [loaded,setLoaded]=useState(false);
  const [taskResult,setTaskResult]=useState(null);

  const sliderValueFormat = (value) => `+${value}%`;

  const getDropDownOptions=(Styles)=>{
    let result=[
      { key: 'header', text: '选择语气', itemType: DropdownMenuItemType.Header },
    ];
    for(const ttsStyle of Styles){
      const item={
        key: ttsStyle.id,
        text: ttsStyle.label,
        data:ttsStyle.desc
      }
      result.push(item)
    }
    return result;
  }

  const dropDownOptions=getDropDownOptions(ttsStyles);

  const onGenerateClick=async ()=>{
    if(text.replace(" ").length===0){
      Toast.fail("文本不为空",2);
    }else{
      const task={
        text:text,rate:rate,style:style
      }
      setLoading(true);
      const response=await generate_tts(task);
      setLoading(false);
      if(response.success){
        setLoaded(true);
        setTaskResult(response.data);
      }else{
        Toast.fail(response.msg,2);
      }
    }
  }

  const onResetClick=()=>{
    setTaskResult(null);
    setLoading(false);
    setLoaded(false);
  }

  return (
    <div>
      <Stack horizontalAlign="center">
        <Stack style={{width:"95vw"}}>
          <Text variant="xLarge" style={{margin:5}}>
            配音生成
          </Text>
        </Stack>
        <TextField
          disabled={loading}
          style={{width:"85vw",maxWidth:800,fontSize:16}}
          label="请输入文本"
          multiline
          maxLength={120}
          autoAdjustHeight
          defaultValue={text}
          onChange={(e,value)=>{
            setText(value)
          }}
        />
        <Stack
          style={{width:"85vw",maxWidth:800,marginTop:10}}
          verticalAlign="center"
          horizontalAlign="start"
          horizontal
          wrap
          tokens={{
            childrenGap:10
          }}
        >
          <Stack style={{width:250}}>
            <Slider
              label="语速"
              max={100}
              min={0}
              step={10}
              defaultValue={rate}
              valueFormat={sliderValueFormat}
              showValue
              onChange={(value,range)=>{
                setRate(value);
              }}
            />
          </Stack>
          <Dropdown
            label="语气"
            defaultSelectedKey={style}
            options={dropDownOptions}
            style={{margin:3}}
            onChanged={(e)=>{
              setStyle(e.key)
              setStyleDesc(e.data)
            }}
          />
        </Stack>
        <Stack
          style={{width:"85vw",maxWidth:800,marginTop:10}}
        >
          <Text
            style={{fontWeight:800}}
          >
            语气说明
          </Text>
          <Text
            style={{margin:5}}
            variant="mediumPlus"
          >
            {styleDesc}
          </Text>
        </Stack>
        <Stack
          style={{width:"85vw",maxWidth:800,marginTop:10}}
          horizontal
          horizontalAlign="start"
          verticalAlign="center"
          tokens={{
            childrenGap:10
          }}
        >
          {
            !loaded&&
            <DefaultButton
              disabled={loading}
              onClick={onGenerateClick}
            >
              生成
            </DefaultButton>
          }
          {
            loaded &&
            <PrimaryButton
              disabled={loading}
              onClick={onResetClick}
            >
              重置
            </PrimaryButton>
          }
          {
            loaded &&
            <DefaultButton
              onClick={()=>{
                document.getElementById('download_video').click();
              }}
            >
              下载视频
            </DefaultButton>
          }
          {
            loaded &&
            <PrimaryButton
              onClick={()=>{
                document.getElementById('download_audio').click();
              }}
            >
              下载mp3
            </PrimaryButton>
          }
          {
            loading&&
            <Stack
              style={{marginLeft:50}}
              horizontalAlign="center"
              verticalAlign="center"
            >
              <Spinner label="正在加载..."/>
            </Stack>
          }
        </Stack>
        {
          taskResult!==null&&taskResult.video!==null&&
          <Stack
            style={{width:"85vw",maxWidth:800,marginTop:10}}
          >
            <Text variant="xLarge">
              <a
                id="download_video"
                href={taskResult.video}
                download={taskResult.video}
              />
              <a
                id="download_audio"
                href={taskResult.audio}
                download={taskResult.audio}
              />
              配音预览
            </Text>
            <Text style={{fontWeight:800,color:"red"}}>
              链接将于{formatDate(taskResult.expires_in*1000)}过期
            </Text>
            <div
              style={{
                maxHeight:isNotMobile()?500:"100%",
                height:isNotMobile()?"60vh":"100%"
              }}
            >
              <Player
                id={taskResult.video}
                sources={{
                  hd: {
                    play_url: taskResult.video
                  }
                }}
                shouldObserveResize
                initialObjectFit={"cover"}
                locale={"zh-Hans"}
              />
            </div>
          </Stack>
        }
      </Stack>
    </div>
  );
}

export default TtsGenerator;
