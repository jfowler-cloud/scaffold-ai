"use client";

import { Canvas } from "@/components/Canvas";
import { Chat } from "@/components/Chat";

export default function Home() {
  return (
    <main className="flex h-screen w-screen">
      {/* Chat Panel - Left Side */}
      <div className="w-[400px] border-r border-border flex flex-col">
        <div className="p-4 border-b border-border">
          <h1 className="text-xl font-semibold">Scaffold AI</h1>
          <p className="text-sm text-muted-foreground">
            Design your application architecture
          </p>
        </div>
        <Chat />
      </div>

      {/* Canvas - Right Side */}
      <div className="flex-1">
        <Canvas />
      </div>
    </main>
  );
}
