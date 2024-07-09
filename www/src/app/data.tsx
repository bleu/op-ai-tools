export const userData = [
  {
    id: 1,
    messages: [],
    name: "Optimism GovGPT",
  },
  // {
  //   id: 2,
  //   name: "John Doe",
  // },
  // {
  //   id: 3,
  //   name: "Elizabeth Smith",
  // },
  // {
  //   id: 4,
  //   name: "John Smith",
  // },
];

export const loggedInUserData = {
  id: 5,
  name: "rpunkt.eth",
};

export type LoggedInUserData = typeof loggedInUserData;

export interface Message {
  id: number;
  name: string;
  message: string;
  timestamp: number;
  isLoading?: boolean;
}

export interface User {
  id: number;
  messages: Message[];
  name: string;
}
