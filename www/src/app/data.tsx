export interface Data {
  answer: string;
  url_supporting: string[];
}
export interface Message {
  id: string;
  name: string;
  data: Data;
  timestamp: number;
  isLoading?: boolean;
}
