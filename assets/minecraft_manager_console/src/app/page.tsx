"use client";
import { useQuery, useMutation, useQueryClient } from "react-query";
import { useRef} from "react";
import { getInstanceInfo, startInstance, stopInstance } from "./api";
import clipboardIcon from "public/clipboardIcon.png";
import LoadingBar, { LoadingBarRef } from "react-top-loading-bar";


export default function HomePage() {

  const loadingRef = useRef<LoadingBarRef>(null);
  
  const queryClient = useQueryClient();
  const { data: instanceInfo, isLoading: isLoading } = useQuery({
    queryFn: getInstanceInfo,
    queryKey: ["instanceInfo"],
    staleTime: 0,
  });

  const { mutateAsync: startInstanceMutation } = useMutation({
    mutationFn: startInstance,
    onSuccess: async () => await refresh(),
  });
  
  const { mutateAsync: stopInstanceMutation } = useMutation({
    mutationFn: stopInstance,
    onSuccess: async () => await refresh(),
  });
  
  async function refresh () {
    loadingRef.current?.continuousStart();
    await queryClient.invalidateQueries(["instanceInfo"]);
    loadingRef.current?.complete();
  }

  const invalidButton = <button className="bg-gray-500 text-white font-bold py-2 px-4 rounded-xl text-4xl w-full">---</button>
  
  const startButton = <button className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-xl text-4xl w-full" onClick={
    async () => await startInstanceMutation()
  }>Start</button>
  
  const stopButton = <button className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded-xl text-4xl w-full" onClick={
    async () => await stopInstanceMutation()
  }>Stop</button>
  
  return (
      <main className="flex min-h-screen flex-col items-center bg-gradient-to-b from-[#2e026d] to-[#15162c] text-white">
        {/* Header */}
        <div className="flex min-w-full bg-sky-800 shadow text-white p-2 rounded-b-xl h-[90px]">
          <LoadingBar color="blue" ref={loadingRef} shadow={true}/>
          <h1 className="flex-grow text-6xl font-bold p-2">Minecraft Manager Console</h1>
          <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-xl text-4xl" onClick={refresh}>Refresh</button>
        </div>

        {/* Content */}
        <div className="flex flex-grow justify-center p-8 gap-8 w-screen">

          {/* Left Column */}
          <div className="flex flex-col items-center w-1/2 h-auto">
            {isLoading ?
              invalidButton
              : instanceInfo?.instanceStatus == "running" ?
                stopButton
                : instanceInfo?.instanceStatus == "stopped" ?
                  startButton
                  : invalidButton
            }

            <div className="bg-slate-950/50 outline outline-offset-2 outline-indigo-900 hover:shadow-2xl text-white p-6 rounded-xl mt-4 w-full h-full">
              <h2 className="text-4xl font-bold text-center mb-7">Virtual Machine</h2>
              <p className="text-2xl">Status: {isLoading ? "..." : instanceInfo?.instanceStatus}</p>
              <p className="flex items-center text-2xl">
                IP: {isLoading ? "..." : instanceInfo?.instanceIP} 
                {instanceInfo?.instanceIP && 
                  <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold p-1 ml-2 rounded-xl" 
                    onClick={async () => await navigator.clipboard.writeText(instanceInfo?.instanceIP ?? "")}>
                    <img className="object-contain max-h-fit" src={clipboardIcon.src} alt="Copy" />
                  </button>
                }
              </p>
            </div>

            <div className="bg-slate-950/50 outline outline-offset-2 outline-indigo-900 hover:shadow-2xl text-white p-6 rounded-xl mt-4 w-full h-full">
              <h2 className="text-4xl font-bold text-center mb-7">Minecraft Server</h2>
              <p className="text-2xl">Status: {isLoading ? "..." : instanceInfo?.serverInfo?.status}</p>
              <p className="text-2xl">MOTD: {isLoading ? "..." : instanceInfo?.serverInfo?.motd}</p>
              <p className="text-2xl">Version: {isLoading ? "..." : instanceInfo?.serverInfo?.version}</p>
              <p className="text-2xl overflow-y-scroll">Players: {isLoading ? "..." : instanceInfo?.serverInfo == null ? "" : "(" + instanceInfo?.serverInfo?.numPlayers + "/" + instanceInfo?.serverInfo?.maxPlayers + ") " + instanceInfo?.serverInfo?.players.join(", ")}</p>
            </div>
          </div>


          {/* Right Column */}
          <div className="flex flex-col-reverse justify-end flex-grow bg-slate-950/50 outline outline-offset-2 outline-indigo-900 hover:shadow-2xl rounded-xl p-8 w-2/3 h-[calc(100vh-160px)]">
            <div className="flex-grow overflow-y-scroll bg-black p-4">
              {isLoading ? "..." : instanceInfo?.serverInfo?.logs.map((log, index) => <p key={index}>{log}</p>)}
            </div>
            <h2 className="text-4xl font-bold text-center mb-7">Logs</h2>
          </div>
        </div>
      </main>
  );
}
