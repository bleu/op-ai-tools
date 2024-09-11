import { create } from "zustand";
import { subscribeWithSelector } from "zustand/middleware";

interface MobileState {
  isMobile: boolean;
  setIsMobile: (isMobile: boolean) => void;
}

const useMobileStore = create<MobileState>()(
  subscribeWithSelector((set) => ({
    isMobile: false,
    setIsMobile: (isMobile: boolean) => set({ isMobile }),
  })),
);

if (typeof window !== "undefined") {
  const checkIfMobile = () => {
    const width = window.innerWidth;
    useMobileStore.getState().setIsMobile(width < 768);
  };

  checkIfMobile();
  window.addEventListener("resize", checkIfMobile);
}

export default useMobileStore;
