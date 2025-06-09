"use client"

import { useState } from "react";
import { ArrowRight } from "lucide-react";

export default function App() {
  const [theme, setTheme] = useState("blue");

  const themes = {
    blue: "bg-blue-500",
    grey: "bg-gray-500",
    red: "bg-red-500",
  };

  return (
    <div className="min-h-screen bg-white flex flex-col items-start p-4">
      {/* Theme Selector */}
      <div className="flex items-center space-x-2 mb-6">
        <span className="text-black font-medium">Select theme:</span>
        {Object.keys(themes).map((color) => (
          <button
            key={color}
            onClick={() => setTheme(color)}
            className={`px-4 py-2 border rounded-md ${
              theme === color ? "border-black" : "border-gray-300"
            }`}
          >
            {color}
          </button>
        ))}
      </div>

      {/* Chat Widget */}
      <div className="relative w-80 h-[500px] shadow-lg rounded-lg overflow-hidden">
        {/* Header */}
        <div
          className={`flex items-center justify-between px-4 py-2 ${themes[theme]}`}
        >
          <div className="flex items-center space-x-2">
            <div className="w-6 h-6 bg-gray-200 rounded-full"></div>
            <span className="text-white font-medium">Operator</span>
          </div>
          <div className="flex items-center space-x-1">
            <span className="text-white text-sm">online</span>
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
          </div>
        </div>

        {/* Chat Body */}
        <div className="flex-1 bg-gray-100 p-4">
          <div className="flex items-start space-x-2">
            <div className="w-6 h-6 bg-gray-200 rounded-full"></div>
            <div>
              <div className="bg-blue-100 text-black text-sm px-3 py-2 rounded-md">
                Hi, how can we help you?
              </div>
              <span className="text-gray-500 text-xs">5/4/25, 6:38 PM</span>
            </div>
          </div>
        </div>

        {/* Input Area */}
        <div className={`flex items-center px-4 py-2 ${themes[theme]}`}>
          <input
            type="text"
            placeholder="Type message..."
            className="flex-1 bg-transparent text-white placeholder-white text-sm outline-none"
          />
          <button className="ml-2">
            <ArrowRight className="text-white" />
          </button>
        </div>
      </div>

      {/* Floating Action Button */}
      <button
        className={`absolute bottom-4 right-4 w-12 h-12 rounded-full flex items-center justify-center text-white shadow-lg ${themes[theme]}`}
      >
        <span className="text-xl">×</span>
      </button>
    </div>
  );
}