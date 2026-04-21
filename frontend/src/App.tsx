import { ReactFlowProvider } from "@xyflow/react";
import { Board } from "./canvas/Board";
import { StatusBar } from "./components/StatusBar";
import { ChatSidebar } from "./components/ChatSidebar";

export function App() {
  return (
    <div className="app">
      <div className="canvas-wrap">
        <StatusBar />
        <ReactFlowProvider>
          <Board />
        </ReactFlowProvider>
      </div>
      <ChatSidebar />
    </div>
  );
}
