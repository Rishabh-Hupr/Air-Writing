def lra(A):
        st=[0]
        top=0
        ns=[A[0]]
        x=len(A)
        for i in range(1,x):
            if A[st[top]]<A[i]:
                ns.append(A[i])
                st.append(i)
                top+=1
            else:
                st.pop(top)
                top-=1
                while top!=-1 and A[st[top]]>A[i]:
                    st.pop(top)
                    top-=1
                if top==-1:
                    ns.append(A[i]*(i+1))
                else:
                    ns.append(A[i]*(i-st[top]))
                st.append(i)
                top+=1
        st.clear()
        st=[x-1]
        top=0
        nr=[A[x-1]]
        for i in range(x-2,-1,-1):
            if A[st[top]]<A[i]:
                nr.append(A[i])
                st.append(i)
                top+=1
            else:
                st.pop(top)
                top-=1
                while top!=-1 and A[st[top]]>A[i]:
                    st.pop(top)
                    top-=1
                if top==-1:
                    nr.append(A[i]*(x-i))
                else:
                    nr.append(A[i]*(st[top]-i))
                st.append(i)
                top+=1
        ans=0
        nr.reverse()
        print(ns)
        print(nr)
        for i in range(x):
            p=ns[i]+nr[i]-A[i]
            if p>ans:
                ans=p
        return ans
t=list(map(int , input().split()))
print(lra(t))
