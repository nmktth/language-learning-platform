import { createSlice, type PayloadAction } from '@reduxjs/toolkit';

interface Course {
  id: number;
  title: string;
  description: string;
}

interface CourseState {
  list: Course[];
  loading: boolean;
}

const initialState: CourseState = {
  list: [],
  loading: false,
};

export const courseSlice = createSlice({
  name: 'courses',
  initialState,
  reducers: {
    setCourses: (state, action: PayloadAction<Course[]>) => {
      state.list = action.payload;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
  },
});

export const { setCourses, setLoading } = courseSlice.actions;
export default courseSlice.reducer;
