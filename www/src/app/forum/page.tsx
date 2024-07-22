import React from "react";

const Sidebar = () => {
  return (
    <div className="w-64 bg-gray-100 p-4">
      <div className="text-xl font-bold mb-4">OPTIMISM GovSummarizer</div>
      <div className="mb-6">
        <h2 className="font-semibold">Feeds</h2>
        <ul>
          <li className="py-2 text-red-500">Trending topics</li>
          <li className="py-2">Forum digest</li>
          <li className="py-2">Latest topics</li>
        </ul>
      </div>
      <div className="mb-6">
        <h2 className="font-semibold">Categories</h2>
        <ul>
          <li className="py-2">All</li>
          <li className="py-2">Delegates</li>
          <li className="py-2">General Discussions</li>
          <li className="py-2">Mission Grants</li>
          <li className="py-2">Updates and Announcements</li>
          <li className="py-2">Retro Funding</li>
          <li className="py-2">Others</li>
        </ul>
      </div>
      <div>
        <h2 className="font-semibold">Have any questions?</h2>
        <div className="text-blue-500 cursor-pointer">Ask GovGPT</div>
      </div>
    </div>
  );
};

const TrendingTopics = () => {
  const topics = [
    {
      title: "Snapshot Proposal",
      category: "Retro Funding",
      status: "Ongoing",
      content: "Content summarized in one paragraph...",
      author: "Author's name",
      readTime: "5 min read",
      date: "Jul 10, 2024",
      lastActivity: "Last activity 5 hours ago",
    },
    // Add more topics here
  ];

  return (
    <div className="flex-1 p-4">
      <h1 className="text-2xl font-bold mb-4">Trending topics</h1>
      <div className="flex justify-between items-center mb-4">
        <div className="text-xl">All</div>
        <div className="relative">
          <button className="bg-gray-200 px-4 py-2 rounded">
            28 Jun 24 - 10 Jul 24
          </button>
        </div>
      </div>
      {topics.map((topic, index) => (
        <div key={index} className="mb-4 p-4 bg-white shadow-md rounded">
          <h2 className="text-xl font-semibold">{topic.title}</h2>
          <div className="flex items-center text-sm mb-2">
            <span className="text-gray-500">{topic.category}</span>
            <span
              className={`ml-2 px-2 py-1 rounded ${
                topic.status === "Ongoing" ? "bg-yellow-200" : "bg-green-200"
              }`}
            >
              {topic.status}
            </span>
            <span className="ml-2 text-blue-500">{topic.author}</span>
          </div>
          <p className="mb-2">{topic.content}</p>
          <div className="flex justify-between text-sm text-gray-500">
            <span>
              {topic.readTime} • {topic.date}
            </span>
            <span>{topic.lastActivity}</span>
          </div>
        </div>
      ))}
    </div>
  );
};

export default function Forum() {
  return (
    <div className="flex">
      <Sidebar />
      <TrendingTopics />
    </div>
  );
}
