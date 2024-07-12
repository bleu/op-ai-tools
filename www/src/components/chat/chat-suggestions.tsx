import { FileText, HelpCircle, PieChart, Vote } from "lucide-react";

export const suggestions = [
  {
    icon: <FileText size={20} />,
    label: "Explain recent proposal",
    value: "Can you explain the most recent Optimism governance proposal?",
  },
  {
    icon: <Vote size={20} />,
    label: "How to vote",
    value: "How can I participate in voting on Optimism governance proposals?",
  },
  {
    icon: <PieChart size={20} />,
    label: "OP token distribution",
    value: "Can you give me an overview of the OP token distribution?",
  },
  {
    icon: <HelpCircle size={20} />,
    label: "Optimism Collective",
    value: "What is the Optimism Collective and how does it work?",
  },
] as const;
