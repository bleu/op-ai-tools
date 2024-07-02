export const userData = [
  {
    id: 1,
    avatar: "/op-logo.png",
    messages: [
      {
        id: 1,
        avatar: "/op-logo.png",
        name: "Optimism GovGPT",
        message: "Hey, Jakob",
      },
      {
        id: 2,
        name: "Jakob Hoeg",
        message: "Hey!",
      },
      {
        id: 3,
        avatar: "/op-logo.png",
        name: "Optimism GovGPT",
        message: "How are you?",
      },
      {
        id: 4,
        name: "Jakob Hoeg",
        message: "I am good, you?",
      },
      {
        id: 5,
        avatar: "/op-logo.png",
        name: "Optimism GovGPT",
        message: "I am good too!",
      },
      {
        id: 6,
        name: "Jakob Hoeg",
        message: "That is good to hear!",
      },
      {
        id: 7,
        avatar: "/op-logo.png",
        name: "Optimism GovGPT",
        message: "How has your day been so far?",
      },
      {
        id: 8,
        name: "Jakob Hoeg",
        message:
          "It has been good. I went for a run this morning and then had a nice breakfast. How about you?",
      },
      {
        id: 9,
        avatar: "/op-logo.png",
        name: "Optimism GovGPT",
        message: "I had a relaxing day. Just catching up on some reading.",
      },
    ],
    name: "Optimism GovGPT",
  },
  {
    id: 2,
    name: "John Doe",
  },
  {
    id: 3,
    name: "Elizabeth Smith",
  },
  {
    id: 4,
    name: "John Smith",
  },
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
