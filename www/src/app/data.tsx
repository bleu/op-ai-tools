export const userData = [
  {
    id: 1,
    avatar: "/op-logo.png",
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

export type UserData = (typeof userData)[number];

export const loggedInUserData = {
  id: 5,
  name: "rpunkt.eth",
};

export type LoggedInUserData = typeof loggedInUserData;

export interface Message {
  id: number;
  avatar?: string;
  name: string;
  message: string;
}

export interface User {
  id: number;
  avatar: string;
  messages: Message[];
  name: string;
}
